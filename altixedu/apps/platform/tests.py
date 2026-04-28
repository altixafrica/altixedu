from datetime import date

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.schools.models import School
from apps.students.models import Student


User = get_user_model()


class PlatformPublicEndpointsTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name='Bright Future Academy',
            subdomain='bright-future',
            email='hello@brightfuture.edu',
            phone='+2348000000000',
            address='12 Marina Road',
            city='Lagos',
            state='Lagos',
            country='Nigeria',
            school_type='private',
            language='en',
        )
        User.objects.create_user(
            username='bright-admin',
            email='admin@brightfuture.edu',
            password='SecurePass123!',
            first_name='Ada',
            last_name='Okafor',
            role='admin',
            school=self.school,
        )
        User.objects.create_user(
            username='bright-teacher',
            email='teacher@brightfuture.edu',
            password='SecurePass123!',
            first_name='Kemi',
            last_name='Balogun',
            role='teacher',
            school=self.school,
        )
        Student.objects.create(
            school=self.school,
            first_name='Tari',
            last_name='Cole',
            admission_number='BF-001',
            date_of_birth=date(2013, 5, 1),
            gender='female',
            enrollment_date=date(2024, 9, 1),
            status='active',
        )

    def test_platform_overview_returns_aggregated_metrics(self):
        response = self.client.get('/api/platform/overview/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['metrics']['active_schools'], 1)
        self.assertEqual(response.data['metrics']['students_managed'], 1)
        self.assertEqual(response.data['metrics']['staff_accounts'], 2)
        self.assertIn('Nigeria', response.data['coverage']['countries'])

    def test_register_school_creates_school_and_admin_with_username(self):
        payload = {
            'name': 'Savannah Public School',
            'subdomain': 'savannah-public',
            'email': 'info@savannah.edu',
            'phone': '+233200000000',
            'city': 'Accra',
            'state': 'Greater Accra',
            'country': 'Ghana',
            'admin_email': 'principal@savannah.edu',
            'admin_password': 'SecurePass123!',
            'admin_first_name': 'Ama',
            'admin_last_name': 'Mensah',
            'timezone': 'Africa/Accra',
            'language': 'en',
            'school_type': 'public',
        }

        response = self.client.post(
            '/api/platform/register-school/',
            payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_school = School.objects.get(subdomain='savannah-public')
        created_admin = User.objects.get(email='principal@savannah.edu')
        self.assertEqual(created_school.name, payload['name'])
        self.assertEqual(created_admin.school, created_school)
        self.assertTrue(created_admin.username)

    def test_platform_health_returns_ok(self):
        response = self.client.get('/api/platform/health/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
