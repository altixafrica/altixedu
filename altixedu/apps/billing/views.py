from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import uuid
from datetime import timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsSchoolAdmin, IsSuperAdmin
from .models import (
    BillingAlert,
    FeatureAccess,
    FreeSchoolPlan,
    Invoice,
    PaymentTransaction,
    Subscription,
    SubscriptionTier,
    UpgradePromotion,
)
from .payment_gateway import FlutterwaveClient, FlutterwaveGatewayError
from .serializers import (
    InvoiceSerializer,
    PaymentTransactionSerializer,
    SubscriptionSerializer,
    SubscriptionTierSerializer,
    UpgradePromotionSerializer,
)

logger = logging.getLogger(__name__)

CURRENCY_CODE = "NGN"


def _as_amount(value) -> Decimal:
    if isinstance(value, Decimal):
        amount = value
    else:
        amount = Decimal(str(value))
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _renewal_delta(payment_frequency: str) -> timedelta:
    if payment_frequency == "quarterly":
        return timedelta(days=90)
    if payment_frequency == "annual":
        return timedelta(days=365)
    return timedelta(days=30)


def _calculate_checkout_amount(tier: SubscriptionTier, payment_frequency: str) -> Decimal:
    monthly_price = _as_amount(tier.monthly_price)

    if payment_frequency == "monthly":
        return monthly_price
    if payment_frequency == "quarterly":
        return _as_amount(monthly_price * Decimal("3") * Decimal("0.95"))
    if payment_frequency == "annual":
        if tier.annual_price:
            return _as_amount(tier.annual_price)
        return _as_amount(monthly_price * Decimal("12") * Decimal("0.85"))
    raise ValueError("Invalid payment frequency")


def _get_government_bulk_discount_percentage(school_count: int) -> int:
    if school_count >= 500:
        return 40
    if school_count >= 101:
        return 30
    if school_count >= 50:
        return 20
    return 0


def _build_government_bulk_pricing():
    brackets = []
    for minimum_schools, label in (
        (1, "Single school or pilot"),
        (50, "State pilot cluster"),
        (101, "Regional rollout"),
        (500, "Statewide deployment"),
    ):
        discount_percentage = _get_government_bulk_discount_percentage(minimum_schools)
        unit_monthly_price = _apply_discount(Decimal("9900.00"), discount_percentage)
        unit_quarterly_price = _as_amount(unit_monthly_price * Decimal("3"))
        unit_annual_price = _as_amount(unit_monthly_price * Decimal("10"))
        brackets.append(
            {
                "minimum_schools": minimum_schools,
                "label": label,
                "discount_percentage": discount_percentage,
                "unit_monthly_price": float(unit_monthly_price),
                "unit_quarterly_price": float(unit_quarterly_price),
                "unit_annual_price": float(unit_annual_price),
            }
        )

    return brackets


def _load_notes(raw_notes: str) -> dict:
    if not raw_notes:
        return {}

    try:
        parsed = json.loads(raw_notes)
    except json.JSONDecodeError:
        return {"raw_notes": raw_notes}

    return parsed if isinstance(parsed, dict) else {"payload": parsed}


def _save_notes(payment_transaction: PaymentTransaction, **updates) -> None:
    notes = _load_notes(payment_transaction.notes)
    notes.update(updates)
    payment_transaction.notes = json.dumps(notes)


def _build_invoice_number() -> str:
    return f"INV-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"


def _get_checkout_promo(promo_code: str | None, tier: SubscriptionTier):
    if not promo_code:
        return None, 0

    try:
        promo = UpgradePromotion.objects.get(code=promo_code.strip())
    except UpgradePromotion.DoesNotExist as exc:
        raise ValueError(f'Promo code "{promo_code}" not found') from exc

    if not promo.is_valid():
        raise ValueError(f'Promo code "{promo_code}" is not active')

    if tier.name not in promo.applicable_tiers:
        raise ValueError(f'Promo code "{promo_code}" does not apply to {tier.display_name}')

    return promo, promo.discount_percentage


def _apply_discount(amount: Decimal, discount_percentage: int) -> Decimal:
    if discount_percentage <= 0:
        return amount
    discount_ratio = Decimal(100 - discount_percentage) / Decimal("100")
    return _as_amount(amount * discount_ratio)


def _ensure_subscription_shell(
    school,
    tier: SubscriptionTier,
    payment_frequency: str,
    discount_percentage: int,
    promo_code: str | None,
) -> Subscription:
    now = timezone.now()
    subscription = Subscription.objects.filter(school=school).first()

    if subscription is None:
        trial_ends_at = now + timedelta(days=max(tier.trial_days, 0))
        subscription = Subscription.objects.create(
            school=school,
            tier=tier,
            monthly_price=tier.monthly_price,
            annual_price=tier.annual_price,
            payment_frequency=payment_frequency,
            status="trial",
            trial_started_at=now,
            trial_ends_at=trial_ends_at,
            renewal_date=now + _renewal_delta(payment_frequency),
            discount_percentage=discount_percentage,
            special_notes=f"Checkout initiated via Flutterwave{f' with promo {promo_code}' if promo_code else ''}",
        )
        return subscription

    subscription.tier = tier
    subscription.monthly_price = tier.monthly_price
    subscription.annual_price = tier.annual_price
    subscription.payment_frequency = payment_frequency
    subscription.discount_percentage = discount_percentage
    subscription.special_notes = (
        f"Pending Flutterwave checkout{f' with promo {promo_code}' if promo_code else ''}"
    )
    subscription.save(
        update_fields=[
            "tier",
            "monthly_price",
            "annual_price",
            "payment_frequency",
            "discount_percentage",
            "special_notes",
        ]
    )
    return subscription


def _serialize_transaction(payment_transaction: PaymentTransaction) -> dict:
    notes = _load_notes(payment_transaction.notes)
    return {
        "reference": payment_transaction.transaction_id,
        "provider_transaction_id": notes.get("flutterwave_transaction_id"),
        "amount": float(payment_transaction.amount),
        "currency": payment_transaction.currency,
        "payment_method": payment_transaction.payment_method,
        "paid_at": payment_transaction.completed_at,
    }


@transaction.atomic
def _finalize_successful_payment(
    payment_transaction: PaymentTransaction,
    verification_data: dict,
) -> Invoice:
    subscription = payment_transaction.subscription
    notes = _load_notes(payment_transaction.notes)
    promo_code = notes.get("promo_code")

    if payment_transaction.status == "completed":
        return Invoice.objects.filter(transaction=payment_transaction).first()

    subscription.status = "active"
    subscription.cancelled_at = None
    subscription.is_trial_converted = True
    subscription.renewal_date = timezone.now() + _renewal_delta(subscription.payment_frequency)
    if not subscription.trial_started_at:
        subscription.trial_started_at = timezone.now()
    subscription.special_notes = (
        f"Active via Flutterwave{f' with promo {promo_code}' if promo_code else ''}"
    )
    subscription.save(
        update_fields=[
            "status",
            "cancelled_at",
            "is_trial_converted",
            "renewal_date",
            "trial_started_at",
            "special_notes",
        ]
    )

    _save_notes(
        payment_transaction,
        flutterwave_transaction_id=str(verification_data.get("id")),
        flutterwave_reference=verification_data.get("flw_ref"),
        payment_type=verification_data.get("payment_type"),
        processor_response=verification_data.get("processor_response"),
        charged_amount=str(verification_data.get("charged_amount", "")),
        verified_status=verification_data.get("status"),
        customer=verification_data.get("customer"),
    )
    payment_transaction.status = "completed"
    payment_transaction.payment_method = "flutterwave"
    payment_transaction.completed_at = timezone.now()
    payment_transaction.save(
        update_fields=["status", "payment_method", "completed_at", "notes"]
    )

    if promo_code and not notes.get("promo_recorded"):
        promo = UpgradePromotion.objects.filter(code=promo_code).first()
        if promo:
            promo.current_uses += 1
            promo.save(update_fields=["current_uses"])
        _save_notes(payment_transaction, promo_recorded=True)
        payment_transaction.save(update_fields=["notes"])

    invoice, created = Invoice.objects.get_or_create(
        transaction=payment_transaction,
        defaults={
            "subscription": subscription,
            "invoice_number": _build_invoice_number(),
            "amount": payment_transaction.amount,
            "due_at": timezone.now(),
            "paid_at": timezone.now(),
            "status": "paid",
        },
    )

    if not created:
        invoice.subscription = subscription
        invoice.amount = payment_transaction.amount
        invoice.due_at = invoice.due_at or timezone.now()
        invoice.paid_at = timezone.now()
        invoice.status = "paid"
        invoice.save(update_fields=["subscription", "amount", "due_at", "paid_at", "status"])

    return invoice


def _mark_payment_failed(payment_transaction: PaymentTransaction, message: str) -> None:
    payment_transaction.status = "failed"
    _save_notes(payment_transaction, failure_reason=message)
    payment_transaction.save(update_fields=["status", "notes"])

    BillingAlert.objects.create(
        subscription=payment_transaction.subscription,
        alert_type="payment_failed",
        message=message,
    )


def _verify_flutterwave_payment(
    payment_transaction: PaymentTransaction,
    flutterwave_transaction_id,
):
    client = FlutterwaveClient()
    verification_response = client.verify_transaction(flutterwave_transaction_id)
    verification_data = verification_response.get("data") or {}

    if str(verification_data.get("tx_ref")) != payment_transaction.transaction_id:
        raise ValueError("Flutterwave transaction reference does not match the checkout request.")

    currency = str(verification_data.get("currency", "")).upper()
    if currency != payment_transaction.currency:
        raise ValueError("Flutterwave payment currency does not match this subscription.")

    try:
        paid_amount = _as_amount(verification_data.get("amount", "0"))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Flutterwave returned an invalid payment amount.") from exc

    if paid_amount < _as_amount(payment_transaction.amount):
        raise ValueError("Flutterwave payment amount is lower than the expected total.")

    if verification_data.get("status") != "successful":
        failure_message = verification_data.get("processor_response") or "Payment was not successful."
        _mark_payment_failed(payment_transaction, failure_message)
        raise ValueError(failure_message)

    invoice = _finalize_successful_payment(payment_transaction, verification_data)
    return verification_data, invoice


class PricingPageView(APIView):
    """Public endpoint for pricing page."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tiers = []
        for tier in SubscriptionTier.objects.all():
            serialized_tier = SubscriptionTierSerializer(tier).data
            serialized_tier["monthly_price"] = float(tier.monthly_price)
            serialized_tier["quarterly_price"] = float(_calculate_checkout_amount(tier, "quarterly"))
            serialized_tier["annual_price"] = float(tier.annual_price) if tier.annual_price else None
            tiers.append(serialized_tier)

        return Response(
            {
                "tiers": tiers,
                "currency": CURRENCY_CODE,
                "note": "Government schools get special pricing and can still pay through Flutterwave.",
                "government_bulk_pricing": _build_government_bulk_pricing(),
            }
        )


class BillingPortfolioView(APIView):
    """Return cross-tenant billing operations data for superadmins."""

    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        subscriptions = list(
            Subscription.objects.select_related("school", "school__ministry", "tier").all()
        )
        invoices = list(
            Invoice.objects.select_related("subscription__school")
            .order_by("-issued_at", "-id")
        )
        transactions = list(
            PaymentTransaction.objects.select_related("subscription__school")
            .order_by("-created_at", "-id")
        )
        alerts = list(
            BillingAlert.objects.select_related("subscription__school")
            .filter(is_resolved=False)
            .order_by("-created_at", "-id")
        )
        promotions = UpgradePromotion.objects.order_by("-starts_at", "-id")

        status_counts = {key: 0 for key, _label in Subscription.STATUS_CHOICES}
        tier_mix = {}
        recent_invoices = InvoiceSerializer(invoices[:8], many=True).data
        recent_transactions = PaymentTransactionSerializer(transactions[:8], many=True).data
        completed_transactions = [transaction for transaction in transactions if transaction.status == "completed"]
        failed_transactions = [transaction for transaction in transactions if transaction.status == "failed"]
        overdue_invoices = [invoice for invoice in invoices if invoice.is_overdue()]
        now = timezone.now()

        latest_invoice_by_subscription = {}
        for invoice in invoices:
            latest_invoice_by_subscription.setdefault(invoice.subscription_id, invoice)

        alert_count_by_subscription = {}
        for alert in alerts:
            alert_count_by_subscription[alert.subscription_id] = (
                alert_count_by_subscription.get(alert.subscription_id, 0) + 1
            )

        estimated_mrr = Decimal("0.00")
        watchlist = []
        renewals_next_30_days = 0

        for subscription in subscriptions:
            status_counts[subscription.status] = status_counts.get(subscription.status, 0) + 1
            tier_name = subscription.tier.display_name if subscription.tier else "Unassigned"
            discounted_monthly_value = _apply_discount(
                _as_amount(subscription.monthly_price or 0),
                subscription.discount_percentage,
            )

            bucket = tier_mix.setdefault(
                tier_name,
                {
                    "tier_name": tier_name,
                    "schools": 0,
                    "active_schools": 0,
                    "trial_schools": 0,
                    "estimated_monthly_value": Decimal("0.00"),
                    "max_students": subscription.tier.max_students if subscription.tier else None,
                    "max_teachers": subscription.tier.max_teachers if subscription.tier else None,
                },
            )
            bucket["schools"] += 1
            if subscription.status == "active":
                bucket["active_schools"] += 1
                bucket["estimated_monthly_value"] += discounted_monthly_value
                estimated_mrr += discounted_monthly_value
            if subscription.status == "trial":
                bucket["trial_schools"] += 1

            days_until_renewal = subscription.days_until_renewal()
            if subscription.status in {"active", "trial", "past_due"} and days_until_renewal <= 30:
                renewals_next_30_days += 1

            latest_invoice = latest_invoice_by_subscription.get(subscription.id)
            unresolved_alerts = alert_count_by_subscription.get(subscription.id, 0)
            needs_attention = (
                subscription.status in {"past_due", "expired", "cancelled"}
                or unresolved_alerts > 0
                or (latest_invoice is not None and latest_invoice.is_overdue())
                or (subscription.status in {"active", "trial"} and days_until_renewal <= 21)
            )

            if needs_attention:
                urgency_score = 0
                if subscription.status == "past_due":
                    urgency_score += 5
                elif subscription.status == "expired":
                    urgency_score += 4
                elif subscription.status == "cancelled":
                    urgency_score += 3
                if latest_invoice is not None and latest_invoice.is_overdue():
                    urgency_score += 3
                if unresolved_alerts:
                    urgency_score += min(unresolved_alerts, 3)
                if days_until_renewal <= 7:
                    urgency_score += 3
                elif days_until_renewal <= 21:
                    urgency_score += 2

                watchlist.append(
                    {
                        "subscription_id": subscription.id,
                        "school_id": subscription.school_id,
                        "school_name": subscription.school.name,
                        "ministry_name": (
                            subscription.school.ministry.name
                            if getattr(subscription.school, "ministry", None)
                            else None
                        ),
                        "tier_name": tier_name,
                        "status": subscription.status,
                        "payment_frequency": subscription.payment_frequency,
                        "renewal_date": subscription.renewal_date,
                        "days_until_renewal": days_until_renewal,
                        "discount_percentage": subscription.discount_percentage,
                        "latest_invoice_number": latest_invoice.invoice_number if latest_invoice else None,
                        "latest_invoice_status": latest_invoice.status if latest_invoice else None,
                        "latest_invoice_amount": float(latest_invoice.amount) if latest_invoice else None,
                        "latest_invoice_due_at": latest_invoice.due_at if latest_invoice else None,
                        "unresolved_alerts": unresolved_alerts,
                        "urgency_score": urgency_score,
                    }
                )

        tier_mix_payload = [
            {
                **bucket,
                "estimated_monthly_value": float(bucket["estimated_monthly_value"]),
            }
            for bucket in sorted(
                tier_mix.values(),
                key=lambda item: (-item["estimated_monthly_value"], item["tier_name"]),
            )
        ]

        watchlist.sort(
            key=lambda item: (
                -item["urgency_score"],
                item["days_until_renewal"],
                item["school_name"].lower(),
            )
        )

        response = {
            "generated_at": now,
            "currency": CURRENCY_CODE,
            "summary": {
                "schools_with_subscriptions": len(subscriptions),
                "active_subscriptions": status_counts.get("active", 0),
                "trial_subscriptions": status_counts.get("trial", 0),
                "past_due_subscriptions": status_counts.get("past_due", 0),
                "cancelled_subscriptions": status_counts.get("cancelled", 0),
                "estimated_monthly_run_rate": float(estimated_mrr),
                "completed_payments_total": float(
                    sum((_as_amount(transaction.amount) for transaction in completed_transactions), Decimal("0.00"))
                ),
                "failed_payments_total": float(
                    sum((_as_amount(transaction.amount) for transaction in failed_transactions), Decimal("0.00"))
                ),
                "renewals_next_30_days": renewals_next_30_days,
                "overdue_invoices": len(overdue_invoices),
                "unresolved_alerts": len(alerts),
                "active_promotions": sum(1 for promotion in promotions if promotion.is_valid()),
            },
            "status_mix": [
                {"status": status_name, "count": count}
                for status_name, count in status_counts.items()
                if count
            ],
            "tier_mix": tier_mix_payload,
            "watchlist": watchlist[:10],
            "recent_transactions": recent_transactions,
            "recent_invoices": recent_invoices,
            "alerts": [
                {
                    "id": alert.id,
                    "school_name": alert.subscription.school.name,
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "created_at": alert.created_at,
                    "email_sent": alert.email_sent,
                    "sms_sent": alert.sms_sent,
                    "whatsapp_sent": alert.whatsapp_sent,
                }
                for alert in alerts[:8]
            ],
            "promotions": UpgradePromotionSerializer(promotions[:6], many=True).data,
            "notes": {
                "estimated_monthly_run_rate": (
                    "Inferred from active subscriptions, current monthly prices, and stored discounts. "
                    "It excludes manual adjustments and one-off invoice items."
                )
            },
        }

        return Response(response)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Manage school subscriptions."""

    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return Subscription.objects.filter(school=self.request.user.school).select_related("tier", "school")

    @action(detail=False, methods=["get"])
    def current(self, request):
        subscription = self.get_queryset().first()
        if subscription is None:
            return Response(
                {"error": "No active subscription"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def check_upgrade_eligibility(self, request):
        subscription = self.get_queryset().first()
        if subscription is None:
            return Response({"eligible": True, "reason": "No subscription yet"})

        if subscription.status in ["trial", "active"]:
            return Response(
                {
                    "eligible": True,
                    "current_tier": subscription.tier.name if subscription.tier else None,
                }
            )

        return Response({"eligible": False, "reason": "Subscription not active"})


class FlutterwaveCheckoutView(APIView):
    """Initialize a hosted Flutterwave checkout session."""

    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def post(self, request):
        school = request.user.school
        if school is None:
            return Response(
                {"error": "Billing checkout requires a school-linked admin account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tier_id = request.data.get("tier_id")
        payment_frequency = request.data.get("payment_frequency", "monthly")
        promo_code = request.data.get("promo_code")

        try:
            tier = SubscriptionTier.objects.get(id=tier_id)
        except SubscriptionTier.DoesNotExist:
            return Response({"error": "Tier not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            promo, discount_percentage = _get_checkout_promo(promo_code, tier)
            amount = _apply_discount(
                _calculate_checkout_amount(tier, payment_frequency),
                discount_percentage,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response(
                {"error": "This plan does not require online payment. Use the free plan flow instead."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = _ensure_subscription_shell(
            school,
            tier,
            payment_frequency,
            discount_percentage,
            promo_code,
        )

        tx_ref = f"altixedu-{school.id}-{uuid.uuid4().hex[:12]}"
        payment_transaction = PaymentTransaction.objects.create(
            subscription=subscription,
            amount=amount,
            currency=CURRENCY_CODE,
            payment_method="flutterwave",
            status="pending",
            transaction_id=tx_ref,
            notes=json.dumps(
                {
                    "tier_id": tier.id,
                    "tier_name": tier.display_name,
                    "payment_frequency": payment_frequency,
                    "discount_percentage": discount_percentage,
                    "promo_code": promo.code if promo else None,
                    "school_id": school.id,
                }
            ),
        )

        try:
            flutterwave_payload = {
                "tx_ref": tx_ref,
                "amount": str(amount),
                "currency": CURRENCY_CODE,
                "redirect_url": f"{settings.FRONTEND_APP_URL.rstrip('/')}/app/billing/callback",
                "customer": {
                    "email": request.user.email,
                    "name": request.user.get_full_name() or request.user.username,
                    "phonenumber": school.phone or request.user.phone or "",
                },
                "customizations": {
                    "title": f"AltixEdu {tier.display_name}",
                    "description": f"{payment_frequency.capitalize()} subscription for {school.name}",
                },
                "meta": {
                    "school_id": school.id,
                    "school_name": school.name,
                    "tier_id": tier.id,
                    "payment_frequency": payment_frequency,
                    "payment_transaction_id": payment_transaction.id,
                },
            }
            flutterwave_response = FlutterwaveClient().initialize_payment(flutterwave_payload)
        except FlutterwaveGatewayError as exc:
            payment_transaction.status = "failed"
            _save_notes(payment_transaction, gateway_error=str(exc), failure_reason=str(exc))
            payment_transaction.save(update_fields=["status", "notes"])
            logger.error("Flutterwave checkout initialization failed for school %s: %s", school.id, exc)
            return Response(
                {"error": str(exc)},
                status=exc.status_code if exc.status_code < 600 else status.HTTP_502_BAD_GATEWAY,
            )

        checkout_data = flutterwave_response.get("data") or {}
        _save_notes(
            payment_transaction,
            checkout_link=checkout_data.get("link"),
            checkout_response=checkout_data,
        )
        payment_transaction.save(update_fields=["notes"])

        return Response(
            {
                "status": "pending",
                "message": "Flutterwave checkout initialized successfully.",
                "checkout_url": checkout_data.get("link"),
                "public_reference": tx_ref,
                "amount": float(amount),
                "currency": CURRENCY_CODE,
                "tier": tier.display_name,
                "payment_frequency": payment_frequency,
                "discount_applied": discount_percentage,
                "next_steps": [
                    "Complete payment on Flutterwave.",
                    "You will be redirected back to the AltixEdu billing callback page.",
                    "The subscription will activate after server-side verification succeeds.",
                ],
            },
            status=status.HTTP_200_OK,
        )


class FlutterwaveVerifyView(APIView):
    """Verify a completed Flutterwave payment and activate the subscription."""

    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def post(self, request):
        tx_ref = request.data.get("tx_ref")
        flutterwave_transaction_id = request.data.get("transaction_id")

        if not tx_ref or not flutterwave_transaction_id:
            return Response(
                {"error": "Both tx_ref and transaction_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_transaction = (
            PaymentTransaction.objects.select_related("subscription", "subscription__tier", "subscription__school")
            .filter(
                transaction_id=tx_ref,
                subscription__school=request.user.school,
            )
            .first()
        )

        if payment_transaction is None:
            return Response(
                {"error": "Payment reference not found for this school."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            verification_data, invoice = _verify_flutterwave_payment(
                payment_transaction,
                flutterwave_transaction_id,
            )
        except FlutterwaveGatewayError as exc:
            logger.error("Flutterwave verification failed for tx_ref %s: %s", tx_ref, exc)
            return Response(
                {"error": str(exc)},
                status=exc.status_code if exc.status_code < 600 else status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError as exc:
            logger.warning("Flutterwave verification rejected for tx_ref %s: %s", tx_ref, exc)
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        subscription_serializer = SubscriptionSerializer(payment_transaction.subscription)
        return Response(
            {
                "status": "verified",
                "message": verification_data.get("processor_response")
                or "Payment verified and subscription activated.",
                "subscription": subscription_serializer.data,
                "transaction": _serialize_transaction(payment_transaction),
                "invoice": {
                    "invoice_number": invoice.invoice_number,
                    "status": invoice.status,
                    "amount": float(invoice.amount),
                }
                if invoice
                else None,
            }
        )


class FlutterwaveWebhookView(APIView):
    """Process Flutterwave webhooks using server-side verification."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        expected_hash = settings.FLUTTERWAVE_SECRET_HASH
        signature_header = request.META.get("HTTP_FLUTTERWAVE_SIGNATURE")
        legacy_hash_header = request.META.get("HTTP_VERIF_HASH") or request.META.get("HTTP_FLW_SIGNATURE")

        if expected_hash:
            if signature_header:
                computed_signature = base64.b64encode(
                    hmac.new(
                        expected_hash.encode("utf-8"),
                        request.body,
                        hashlib.sha256,
                    ).digest()
                ).decode("utf-8")
                if not hmac.compare_digest(computed_signature, signature_header):
                    return Response(
                        {"error": "Invalid webhook signature"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            elif legacy_hash_header:
                if legacy_hash_header != expected_hash:
                    return Response(
                        {"error": "Invalid webhook signature"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                return Response(
                    {"error": "Missing webhook signature"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        payload = request.data if isinstance(request.data, dict) else {}
        event_data = payload.get("data") or {}
        tx_ref = event_data.get("tx_ref")
        flutterwave_transaction_id = event_data.get("id")

        if not tx_ref or not flutterwave_transaction_id:
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)

        payment_transaction = (
            PaymentTransaction.objects.select_related("subscription", "subscription__tier", "subscription__school")
            .filter(transaction_id=tx_ref)
            .first()
        )

        if payment_transaction is None:
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)

        try:
            _verify_flutterwave_payment(payment_transaction, flutterwave_transaction_id)
        except Exception as exc:  # keep webhook response stable while logging details
            logger.warning("Flutterwave webhook verification failed for tx_ref %s: %s", tx_ref, exc)
            return Response({"status": "ignored"}, status=status.HTTP_200_OK)

        return Response({"status": "processed"}, status=status.HTTP_200_OK)


class UpgradeDowngradeView(APIView):
    """Handle tier changes."""

    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def post(self, request):
        school = request.user.school
        new_tier_id = request.data.get("new_tier_id")
        effective_date = request.data.get("effective_date", "immediate")

        try:
            subscription = Subscription.objects.get(school=school)
            new_tier = SubscriptionTier.objects.get(id=new_tier_id)
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription"}, status=status.HTTP_404_NOT_FOUND)
        except SubscriptionTier.DoesNotExist:
            return Response({"error": "Tier not found"}, status=status.HTTP_404_NOT_FOUND)

        old_tier = subscription.tier

        if effective_date == "immediate":
            now = timezone.now()
            days_remaining = max((subscription.renewal_date - now).days, 0)

            old_daily_rate = float(old_tier.monthly_price) / 30 if old_tier else 0
            new_daily_rate = float(new_tier.monthly_price) / 30
            proration_credit = old_daily_rate * days_remaining
            proration_charge = new_daily_rate * days_remaining
            prorated_amount = proration_charge - proration_credit

            subscription.tier = new_tier
            subscription.monthly_price = new_tier.monthly_price
            subscription.annual_price = new_tier.annual_price
            subscription.save(update_fields=["tier", "monthly_price", "annual_price"])

            return Response(
                {
                    "status": "success",
                    "message": "Tier updated immediately. Charge collection can be handled in a new Flutterwave checkout if needed.",
                    "old_tier": old_tier.display_name if old_tier else None,
                    "new_tier": new_tier.display_name,
                    "prorated_amount": float(prorated_amount),
                    "next_billing_cycle": subscription.renewal_date.date(),
                }
            )

        BillingAlert.objects.create(
            subscription=subscription,
            alert_type="upgrade_suggested",
            message=(
                f"Tier change from {old_tier.display_name if old_tier else 'current'} "
                f"to {new_tier.display_name} scheduled for {subscription.renewal_date.date()}"
            ),
        )

        return Response(
            {
                "status": "scheduled",
                "message": f"Tier will change to {new_tier.display_name} on next renewal",
                "renewal_date": subscription.renewal_date.date(),
            }
        )


class CancelSubscriptionView(APIView):
    """Cancel the current subscription and move the school to the free tier."""

    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def post(self, request):
        school = request.user.school
        reason = request.data.get("reason", "No reason provided")

        try:
            subscription = Subscription.objects.get(school=school)
            free_tier = SubscriptionTier.objects.get(name="free")
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription"}, status=status.HTTP_404_NOT_FOUND)
        except SubscriptionTier.DoesNotExist:
            return Response(
                {"error": "Free tier is not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        subscription.status = "cancelled"
        subscription.cancelled_at = timezone.now()
        subscription.tier = free_tier
        subscription.monthly_price = free_tier.monthly_price
        subscription.annual_price = free_tier.annual_price
        subscription.discount_percentage = 0
        subscription.special_notes = f"Cancelled by admin. Reason: {reason}"
        subscription.save(
            update_fields=[
                "status",
                "cancelled_at",
                "tier",
                "monthly_price",
                "annual_price",
                "discount_percentage",
                "special_notes",
            ]
        )

        FreeSchoolPlan.objects.get_or_create(school=school)
        logger.info("School %s cancelled subscription. Reason: %s", school.id, reason)

        return Response(
            {
                "status": "success",
                "message": "Subscription cancelled. The school is now on the free tier.",
                "remaining_access": f"Until {subscription.cancelled_at:%Y-%m-%d}",
                "free_tier_info": {
                    "max_students": free_tier.max_students,
                    "features": list(
                        FeatureAccess.objects.filter(tier=free_tier, is_enabled=True).values_list(
                            "feature",
                            flat=True,
                        )
                    ),
                },
            }
        )


class PaymentHistoryView(APIView):
    """Return payment history for the current school."""

    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        subscription = Subscription.objects.filter(school=request.user.school).first()
        if subscription is None:
            return Response({"error": "No subscription"}, status=status.HTTP_404_NOT_FOUND)

        transactions = PaymentTransaction.objects.filter(subscription=subscription).order_by("-created_at")
        serializer = PaymentTransactionSerializer(transactions, many=True)
        summary = transactions.aggregate(
            total_paid=Sum("amount", filter=Q(status="completed")),
            total_failed=Sum("amount", filter=Q(status="failed")),
            total_transactions=Count("id"),
            completed_transactions=Count("id", filter=Q(status="completed")),
        )

        return Response(
            {
                "transactions": serializer.data,
                "summary": {
                    "total_paid": float(summary["total_paid"] or 0),
                    "total_failed": float(summary["total_failed"] or 0),
                    "total_transactions": summary["total_transactions"] or 0,
                    "completed_transactions": summary["completed_transactions"] or 0,
                },
            }
        )


class InvoiceView(APIView):
    """Return invoices for the current school."""

    permission_classes = [permissions.IsAuthenticated, IsSchoolAdmin]

    def get(self, request):
        subscription = Subscription.objects.filter(school=request.user.school).first()
        if subscription is None:
            return Response({"error": "No subscription"}, status=status.HTTP_404_NOT_FOUND)

        invoice_id = request.query_params.get("invoice_id")
        if invoice_id:
            try:
                invoice = Invoice.objects.get(id=invoice_id, subscription=subscription)
            except Invoice.DoesNotExist:
                return Response({"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response(
                {
                    "invoice_number": invoice.invoice_number,
                    "amount": float(invoice.amount),
                    "issued_at": invoice.issued_at,
                    "due_at": invoice.due_at,
                    "status": invoice.status,
                    "paid_at": invoice.paid_at,
                }
            )

        invoices = Invoice.objects.filter(subscription=subscription).order_by("-issued_at")
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
