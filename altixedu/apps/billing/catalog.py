from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from .models import FeatureAccess, SubscriptionTier

ALL_FEATURES = [choice[0] for choice in FeatureAccess.FEATURE_CHOICES]

DEFAULT_BILLING_CATALOG = [
    {
        "name": "free",
        "display_name": "Free Plan",
        "monthly_price": Decimal("0.00"),
        "annual_price": None,
        "max_students": 120,
        "max_teachers": 20,
        "max_classrooms": 12,
        "support_level": "email",
        "trial_days": 0,
        "feature_flags": {
            "attendance": True,
            "grades": True,
            "messaging": True,
            "student_portal": True,
        },
        "enabled_features": [
            "attendance",
            "grades",
            "messaging",
            "student_portal",
        ],
    },
    {
        "name": "starter",
        "display_name": "Starter Plan",
        "monthly_price": Decimal("9900.00"),
        "annual_price": Decimal("99000.00"),
        "max_students": 999999,
        "max_teachers": 20,
        "max_classrooms": 24,
        "support_level": "email",
        "trial_days": 14,
        "feature_flags": {
            "attendance": True,
            "grades": True,
            "fees": True,
            "messaging": True,
            "ai_alerts": True,
        },
        "enabled_features": [
            "attendance",
            "grades",
            "fees",
            "messaging",
            "ai_alerts",
        ],
    },
    {
        "name": "growth",
        "display_name": "Professional Plan",
        "monthly_price": Decimal("19900.00"),
        "annual_price": Decimal("199000.00"),
        "max_students": 999999,
        "max_teachers": 999999,
        "max_classrooms": 80,
        "support_level": "phone",
        "trial_days": 21,
        "feature_flags": {
            "attendance": True,
            "grades": True,
            "fees": True,
            "messaging": True,
            "student_portal": True,
            "advanced_reports": True,
            "ai_alerts": True,
            "sms_alerts": True,
            "api_access": True,
        },
        "enabled_features": [
            "attendance",
            "grades",
            "fees",
            "messaging",
            "student_portal",
            "advanced_reports",
            "ai_alerts",
            "sms_alerts",
            "api_access",
        ],
    },
    {
        "name": "scale",
        "display_name": "Enterprise Plan",
        "monthly_price": Decimal("39900.00"),
        "annual_price": Decimal("399000.00"),
        "max_students": 999999,
        "max_teachers": 999999,
        "max_classrooms": 250,
        "support_level": "vip",
        "trial_days": 30,
        "feature_flags": {
            "attendance": True,
            "grades": True,
            "fees": True,
            "messaging": True,
            "student_portal": True,
            "advanced_reports": True,
            "ai_alerts": True,
            "sms_alerts": True,
            "api_access": True,
            "custom_integration": True,
        },
        "enabled_features": [
            "attendance",
            "grades",
            "fees",
            "messaging",
            "student_portal",
            "advanced_reports",
            "ai_alerts",
            "sms_alerts",
            "api_access",
            "custom_integration",
        ],
    },
    {
        "name": "govt",
        "display_name": "Government Bulk Plan",
        "monthly_price": Decimal("9900.00"),
        "annual_price": Decimal("99000.00"),
        "max_students": 999999,
        "max_teachers": 999999,
        "max_classrooms": 999999,
        "support_level": "vip",
        "trial_days": 30,
        "feature_flags": {
            "attendance": True,
            "grades": True,
            "fees": True,
            "messaging": True,
            "bulk_import": True,
            "student_portal": True,
            "advanced_reports": True,
            "pdf_export": True,
            "ai_alerts": True,
            "sms_alerts": True,
            "api_access": True,
            "custom_integration": True,
        },
        "enabled_features": [
            "attendance",
            "grades",
            "fees",
            "messaging",
            "bulk_import",
            "student_portal",
            "advanced_reports",
            "pdf_export",
            "ai_alerts",
            "sms_alerts",
            "api_access",
            "custom_integration",
        ],
    },
]


@transaction.atomic
def seed_default_billing_catalog():
    seeded_tiers = []

    for definition in DEFAULT_BILLING_CATALOG:
        enabled_features = set(definition["enabled_features"])
        tier_defaults = {
            "display_name": definition["display_name"],
            "monthly_price": definition["monthly_price"],
            "annual_price": definition["annual_price"],
            "max_students": definition["max_students"],
            "max_teachers": definition["max_teachers"],
            "max_classrooms": definition["max_classrooms"],
            "features": definition["feature_flags"],
            "support_level": definition["support_level"],
            "trial_days": definition["trial_days"],
        }
        tier, _created = SubscriptionTier.objects.update_or_create(
            name=definition["name"],
            defaults=tier_defaults,
        )

        for feature in ALL_FEATURES:
            FeatureAccess.objects.update_or_create(
                tier=tier,
                feature=feature,
                defaults={"is_enabled": feature in enabled_features},
            )

        seeded_tiers.append(tier)

    return seeded_tiers
