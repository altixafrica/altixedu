#!/usr/bin/env python
"""
Seed dashboard data for E2E tests:
1. Create subscription data for superadmin billing portfolio
2. Create ministry dashboard aggregation data
3. Populate watchlist items
"""

import os
import sys
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
sys.path.insert(0, '/c/Users/pc/Documents/altixedu-backend/altixedu')
django.setup()

from django.utils import timezone
from apps.schools.models import School, Ministry
from apps.billing.models import SubscriptionTier, Subscription, PaymentTransaction
from apps.government.models import MinistryDashboardAggregation, MinistryDashboardAlert


def seed_subscription_tiers():
    """Create subscription tiers if they don't exist"""
    print("Creating subscription tiers...")
    
    tiers = [
        {
            'name': 'starter',
            'display_name': 'Starter Plan',
            'monthly_price': 5000,
            'annual_price': 50000,
            'max_students': 200,
            'max_teachers': 20,
            'support_level': 'email',
            'features': {'attendance': True, 'messaging': True, 'basic_reports': True}
        },
        {
            'name': 'growth',
            'display_name': 'Growth Plan',
            'monthly_price': 15000,
            'annual_price': 150000,
            'max_students': 500,
            'max_teachers': 50,
            'support_level': 'chat',
            'features': {'attendance': True, 'messaging': True, 'advanced_reports': True, 'integration': True}
        },
        {
            'name': 'scale',
            'display_name': 'Scale Plan',
            'monthly_price': 50000,
            'annual_price': 500000,
            'max_students': 2000,
            'max_teachers': 200,
            'support_level': 'phone',
            'features': {'attendance': True, 'messaging': True, 'advanced_reports': True, 'integration': True, 'api': True}
        },
    ]
    
    for tier_data in tiers:
        tier, created = SubscriptionTier.objects.get_or_create(
            name=tier_data['name'],
            defaults=tier_data
        )
        if created:
            print(f"  ✓ Created {tier.display_name}")
        else:
            print(f"  ✓ {tier.display_name} already exists")
    
    return SubscriptionTier.objects.all()


def seed_subscriptions():
    """Create subscriptions for schools"""
    print("\nCreating subscriptions...")
    
    # Get tiers
    starter_tier = SubscriptionTier.objects.get(name='starter')
    growth_tier = SubscriptionTier.objects.get(name='growth')
    scale_tier = SubscriptionTier.objects.get(name='scale')
    
    # Get schools (or create if needed)
    schools = School.objects.all()[:5]
    if not schools:
        print("  ⚠ No schools found in database")
        return
    
    tiers = [starter_tier, growth_tier, scale_tier, starter_tier, growth_tier]
    
    for school, tier in zip(schools, tiers):
        subscription, created = Subscription.objects.get_or_create(
            school=school,
            defaults={
                'tier': tier,
                'monthly_price': tier.monthly_price,
                'status': 'active',
                'renewal_date': timezone.now() + timedelta(days=30),
                'payment_frequency': 'monthly'
            }
        )
        
        if created:
            print(f"  ✓ Created subscription for {school.name} ({tier.display_name})")
            
            # Create a sample payment transaction
            PaymentTransaction.objects.create(
                subscription=subscription,
                amount=tier.monthly_price,
                currency='NGN',
                payment_method='bank_transfer',
                status='completed',
                transaction_id=f'txn_{school.id}_{timezone.now().timestamp()}',
                completed_at=timezone.now()
            )
            print(f"    → Created payment transaction for {school.name}")
        else:
            print(f"  ✓ Subscription for {school.name} already exists")


def seed_ministry_dashboard():
    """Create ministry dashboard aggregation data"""
    print("\nCreating ministry dashboard aggregation...")
    
    # Get or create ministry
    ministry, _ = Ministry.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Test Ministry',
            'state_or_province': 'Lagos',
            'country': 'Nigeria',
            'currency_code': 'NGN'
        }
    )
    
    dashboard, created = MinistryDashboardAggregation.objects.get_or_create(
        state='Lagos',
        ministry=ministry,
        defaults={
            'total_schools': 25,
            'schools_live': 23,
            'schools_pending': 2,
            'avg_deployment_days': 4.2,
            'total_students': 8500,
            'total_fees_collected': 42500000,
            'total_fees_outstanding': 8750000,
            'collection_rate_percentage': 82.9,
            'avg_fee_per_student': 5000,
            'total_teachers': 450,
            'teachers_active_system': 438,
            'teachers_last_7_days': 412,
            'avg_teacher_weekly_hours': 22.5,
            'total_admin_hours_saved_weekly': 156.75,
            'avg_attendance_rate': 87.3,
            'schools_below_attendance_threshold': 2,
            'overall_pass_rate': 78.4,
            'students_at_risk_count': 285,
        }
    )
    
    if created:
        print(f"  ✓ Created ministry dashboard for {ministry.name} ({ministry.state_or_province})")
        
        # Create sample alerts
        MinistryDashboardAlert.objects.create(
            dashboard=dashboard,
            level='warning',
            title='Collection Rate Below Target',
            description='Lagos state collection rate is 82.9%, target is 90%',
            metric_type='collection',
            metric_value=82.9,
            threshold=90.0
        )
        print(f"    → Created alert for collection rate")
        
        MinistryDashboardAlert.objects.create(
            dashboard=dashboard,
            level='success',
            title='Attendance Rate Improvement',
            description='Average attendance improved to 87.3% from 84.2% last month',
            metric_type='attendance',
            metric_value=87.3,
            threshold=85.0
        )
        print(f"    → Created alert for attendance improvement")
        
    else:
        print(f"  ✓ Ministry dashboard for {ministry.name} already exists")


def main():
    print("=" * 60)
    print("SEEDING DASHBOARD DATA FOR E2E TESTS")
    print("=" * 60)
    
    try:
        seed_subscription_tiers()
        seed_subscriptions()
        seed_ministry_dashboard()
        
        print("\n" + "=" * 60)
        print("✅ Dashboard data seeded successfully!")
        print("=" * 60)
        print("\nYou can now run E2E tests:")
        print("  npm run test:e2e")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
