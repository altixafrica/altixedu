from datetime import timedelta

from django.utils import timezone

from .models import FreeSchoolPlan, Subscription, SubscriptionTier


def get_default_tier_for_school(school):
    """
    Default ministry-linked and public schools to the government tier when
    available so every provisioned network school lands on a billable track.
    Other schools start on the free tier unless the catalog is incomplete.
    """
    if school.ministry_id or school.school_type == 'public':
        govt_tier = SubscriptionTier.objects.filter(name='govt').first()
        if govt_tier:
            return govt_tier

        fallback_billable_tier = SubscriptionTier.objects.exclude(name='free').order_by('monthly_price').first()
        if fallback_billable_tier:
            return fallback_billable_tier

    free_tier = SubscriptionTier.objects.filter(name='free').first()
    if free_tier:
        return free_tier

    return SubscriptionTier.objects.order_by('monthly_price').first()


def seed_school_subscription(school):
    """
    Ensure every provisioned school has a subscription shell so billing and plan pages work.
    """
    if Subscription.objects.filter(school=school).exists():
        return Subscription.objects.get(school=school)

    tier = get_default_tier_for_school(school)
    if tier is None:
        return None

    now = timezone.now()
    payment_frequency = 'annual' if tier.name == 'govt' else 'monthly'
    renewal_days = 365 if payment_frequency == 'annual' else 30

    if tier.name == 'free':
        status = 'active'
        trial_started_at = None
        trial_ends_at = None
        notes = 'Provisioned on free tier during school creation.'
    else:
        status = 'trial'
        trial_started_at = now
        trial_ends_at = now + timedelta(days=max(tier.trial_days, 0))
        if school.ministry_id:
            notes = 'Provisioned with ministry-linked billing shell during school creation.'
        else:
            notes = 'Provisioned with subscription shell during school creation.'

    subscription = Subscription.objects.create(
        school=school,
        tier=tier,
        monthly_price=tier.monthly_price,
        annual_price=tier.annual_price,
        payment_frequency=payment_frequency,
        status=status,
        trial_started_at=trial_started_at,
        trial_ends_at=trial_ends_at,
        renewal_date=now + timedelta(days=renewal_days),
        special_notes=notes,
    )

    if tier.name == 'free':
        FreeSchoolPlan.objects.get_or_create(school=school)

    return subscription
