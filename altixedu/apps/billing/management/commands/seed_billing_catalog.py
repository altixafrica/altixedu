from django.core.management.base import BaseCommand

from apps.billing.catalog import DEFAULT_BILLING_CATALOG, seed_default_billing_catalog
from apps.billing.views import _calculate_checkout_amount


class Command(BaseCommand):
    help = "Seed the default AltixEdu billing catalog with pricing tiers and feature access."

    def handle(self, *args, **options):
        tiers = seed_default_billing_catalog()
        self.stdout.write(self.style.SUCCESS("Seeded AltixEdu billing catalog."))

        for tier in tiers:
            quarterly_amount = _calculate_checkout_amount(tier, "quarterly")
            annual_amount = tier.annual_price or _calculate_checkout_amount(tier, "annual")
            self.stdout.write(
                f"- {tier.display_name}: monthly NGN {tier.monthly_price:,.0f}, "
                f"quarterly NGN {quarterly_amount:,.0f}, annual NGN {annual_amount:,.0f}"
            )

        self.stdout.write(
            f"Catalog contains {len(DEFAULT_BILLING_CATALOG)} tiers and is safe to rerun."
        )
