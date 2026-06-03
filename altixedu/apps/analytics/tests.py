from django.test import TestCase
from apps.analytics.models import AnalyticsDashboard, SchoolPerformanceMetric
from apps.schools.models import School


class AnalyticsTestCase(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Test School',
            subdomain='testschool',
            country='Nigeria'
        )

    def test_analytics_dashboard_creation(self):
        dashboard = AnalyticsDashboard.objects.create(
            school=self.school,
            total_students=100,
            students_at_risk_count=10,
            collection_rate_percentage=85.5
        )
        self.assertEqual(dashboard.total_students, 100)
        self.assertEqual(dashboard.students_at_risk_count, 10)
