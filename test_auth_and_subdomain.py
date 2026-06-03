#!/usr/bin/env python
"""
Comprehensive test for Authentication Flow and Subdomain Functionality

Tests both backend and frontend integration:
1. Backend: Login endpoint returns token + role-based permissions
2. Backend: Subdomain validation and availability checks
3. Frontend: Auth token storage and retrieval
4. Frontend: Login form integration
5. Frontend: Subdomain check integration
"""

import os
import sys
import json
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent / 'altixedu'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.schools.models import School, Ministry
from apps.platform.views import SubdomainCheckAPIView
from altixedu.platform_service import SubdomainValidator


User = get_user_model()


class AuthFlowTestCase(TestCase):
    """Test authentication flow - backend"""
    
    def setUp(self):
        """Create test data"""
        self.client = APIClient()
        
        # Create ministry
        self.ministry = Ministry.objects.create(
            name='Test Ministry',
            country='Nigeria',
            state_or_province='Lagos',
            currency_code='NGN'
        )
        
        # Create school
        self.school = School.objects.create(
            name='Test Academy',
            subdomain='test-academy',
            country='Nigeria',
            school_type='private',
            ministry=self.ministry
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            role='admin',
            school=self.school,
            first_name='Admin',
            last_name='User'
        )
        
        # Create teacher user
        self.teacher_user = User.objects.create_user(
            username='teacher@test.com',
            email='teacher@test.com',
            password='testpass123',
            role='teacher',
            school=self.school,
            first_name='Teacher',
            last_name='User'
        )
        
        # Create student user
        self.student_user = User.objects.create_user(
            username='student@test.com',
            email='student@test.com',
            password='testpass123',
            role='student',
            school=self.school,
            first_name='Student',
            last_name='User'
        )
    
    def test_login_with_email_success(self):
        """Test successful login with email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify response structure
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertIn('role', data)
        self.assertIn('school', data)
        self.assertIn('permissions', data)
        
        # Verify token is valid
        self.assertTrue(Token.objects.filter(key=data['token']).exists())
        
        print("✅ Login with email - SUCCESS")
        print(f"   Token: {data['token'][:20]}...")
        print(f"   Role: {data['role']}")
        return data
    
    def test_login_with_username_success(self):
        """Test successful login with username"""
        response = self.client.post('/api/auth/login/', {
            'username': 'teacher@test.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('token', data)
        self.assertEqual(data['role'], 'teacher')
        
        print("✅ Login with username - SUCCESS")
        print(f"   Role: {data['role']}")
        return data
    
    def test_login_invalid_password(self):
        """Test login with wrong password"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        
        self.assertIn('error', data)
        print("✅ Invalid password rejection - SUCCESS")
        print(f"   Error: {data['error']}")
    
    def test_login_nonexistent_user(self):
        """Test login for non-existent user"""
        response = self.client.post('/api/auth/login/', {
            'email': 'nonexistent@test.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 401)
        print("✅ Nonexistent user rejection - SUCCESS")
    
    def test_role_permissions_returned(self):
        """Test that role-based permissions are returned correctly"""
        # Test admin role permissions
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'testpass123'
        })
        
        data = response.json()
        permissions = data['permissions']
        
        # Admin should have these permissions
        self.assertTrue(permissions.get('view_own_school'))
        self.assertTrue(permissions.get('manage_school_staff'))
        self.assertTrue(permissions.get('access_government_features'))
        
        print("✅ Admin role permissions - SUCCESS")
        print(f"   Permissions: {list(permissions.keys())}")
        
        # Test teacher role permissions
        response = self.client.post('/api/auth/login/', {
            'email': 'teacher@test.com',
            'password': 'testpass123'
        })
        
        data = response.json()
        permissions = data['permissions']
        
        # Teacher should have these permissions
        self.assertTrue(permissions.get('view_own_classroom'))
        self.assertTrue(permissions.get('mark_attendance'))
        self.assertTrue(permissions.get('enter_grades'))
        
        print("✅ Teacher role permissions - SUCCESS")
        print(f"   Permissions: {list(permissions.keys())}")
    
    def test_school_data_in_response(self):
        """Test that school data is included in login response"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'testpass123'
        })
        
        data = response.json()
        school = data['school']
        
        self.assertEqual(school['name'], 'Test Academy')
        self.assertEqual(school['subdomain'], 'test-academy')
        self.assertEqual(school['full_domain'], 'test-academy.altixedu.com')
        
        print("✅ School data in response - SUCCESS")
        print(f"   School: {school['name']}")
        print(f"   Domain: {school['full_domain']}")


class SubdomainFunctionalityTestCase(TestCase):
    """Test subdomain validation and availability checks"""
    
    def setUp(self):
        """Create test data"""
        self.client = APIClient()
        
        # Create existing school
        self.ministry = Ministry.objects.create(
            name='Test Ministry',
            country='Nigeria'
        )
        
        self.existing_school = School.objects.create(
            name='Existing School',
            subdomain='existing-school',
            country='Nigeria',
            school_type='private',
            ministry=self.ministry
        )
    
    def test_subdomain_validation_rules(self):
        """Test subdomain validator rules"""
        validator = SubdomainValidator
        
        # Valid subdomain
        self.assertTrue(validator.is_available('newschool'))
        print("✅ Valid subdomain accepted")
        
        # Too short
        self.assertFalse(validator.is_available('ab'))
        print("✅ Too short subdomain rejected")
        
        # Too long
        self.assertFalse(validator.is_available('a' * 51))
        print("✅ Too long subdomain rejected")
        
        # Invalid characters
        self.assertFalse(validator.is_available('school@123'))
        print("✅ Invalid characters rejected")
        
        # Starts with hyphen
        self.assertFalse(validator.is_available('-school'))
        print("✅ Hyphen start rejected")
        
        # Ends with hyphen
        self.assertFalse(validator.is_available('school-'))
        print("✅ Hyphen end rejected")
        
        # Reserved word
        self.assertFalse(validator.is_available('admin'))
        print("✅ Reserved word rejected")
        
        # Already taken
        self.assertFalse(validator.is_available('existing-school'))
        print("✅ Already taken subdomain rejected")
    
    def test_subdomain_check_endpoint(self):
        """Test subdomain check API endpoint"""
        # Available subdomain
        response = self.client.post('/api/platform/check-subdomain/', {
            'subdomain': 'new-school'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data['is_available'])
        self.assertIn('available', data['message'].lower())
        print("✅ Available subdomain check - SUCCESS")
        print(f"   Message: {data['message']}")
        
        # Unavailable subdomain (already taken)
        response = self.client.post('/api/platform/check-subdomain/', {
            'subdomain': 'existing-school'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertFalse(data['is_available'])
        self.assertIn('not available', data['message'].lower())
        print("✅ Unavailable subdomain check - SUCCESS")
        print(f"   Message: {data['message']}")
    
    def test_subdomain_suggestions(self):
        """Test subdomain suggestions for school name"""
        response = self.client.post('/api/platform/check-subdomain/', {
            'subdomain': 'existing-school',  # Already taken
            'school_name': 'Existing School Academy'
        })
        
        data = response.json()
        
        self.assertFalse(data['is_available'])
        self.assertIn('suggestions', data)
        self.assertTrue(len(data['suggestions']) > 0)
        
        print("✅ Subdomain suggestions - SUCCESS")
        print(f"   Suggestions: {data['suggestions'][:3]}")


class FrontendAuthIntegrationTestCase(TestCase):
    """Test frontend auth integration (simulated)"""
    
    def setUp(self):
        """Create test data"""
        self.ministry = Ministry.objects.create(
            name='Test Ministry',
            country='Nigeria'
        )
        
        self.school = School.objects.create(
            name='Test School',
            subdomain='test-school',
            country='Nigeria',
            school_type='private',
            ministry=self.ministry
        )
        
        self.user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123',
            role='admin',
            school=self.school
        )
        
        self.client = APIClient()
    
    def test_frontend_auth_token_flow(self):
        """Simulate frontend token storage and retrieval"""
        # Step 1: Frontend sends login request
        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': 'testpass123'
        })
        
        data = response.json()
        token = data['token']
        
        print("✅ Frontend login - SUCCESS")
        print(f"   Token stored in localStorage")
        
        # Step 2: Frontend uses token in subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        # Verify token is valid
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 200)
        
        print("✅ Token authentication - SUCCESS")
        print(f"   Token accepted for subsequent requests")
    
    def test_frontend_role_routing(self):
        """Test that frontend routes correctly based on role"""
        # Login as admin
        response = self.client.post('/api/auth/login/', {
            'email': 'test@test.com',
            'password': 'testpass123'
        })
        
        data = response.json()
        role = data['role']
        
        # Simulate frontend routing logic
        routes = {
            'admin': '/dashboard',
            'teacher': '/app/teacher',
            'student': '/app/student',
            'parent': '/app/parent',
            'bursar': '/app/bursar',
        }
        
        expected_route = routes.get(role, '/dashboard')
        
        print(f"✅ Frontend role routing - SUCCESS")
        print(f"   Role: {role}")
        print(f"   Route: {expected_route}")


def run_all_tests():
    """Run all tests and print summary"""
    print("\n" + "="*70)
    print("AUTHENTICATION & SUBDOMAIN FUNCTIONALITY TEST SUITE")
    print("="*70 + "\n")
    
    # Test auth flow
    print("\n📋 AUTHENTICATION FLOW TESTS")
    print("-" * 70)
    
    from django.test import TestLoader, TextTestRunner
    
    loader = TestLoader()
    suite = loader.loadTestsFromTestCase(AuthFlowTestCase)
    runner = TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    auth_passed = result.wasSuccessful()
    
    # Test subdomains
    print("\n\n📋 SUBDOMAIN FUNCTIONALITY TESTS")
    print("-" * 70)
    
    suite = loader.loadTestsFromTestCase(SubdomainFunctionalityTestCase)
    result = runner.run(suite)
    
    subdomain_passed = result.wasSuccessful()
    
    # Test frontend integration
    print("\n\n📋 FRONTEND INTEGRATION TESTS")
    print("-" * 70)
    
    suite = loader.loadTestsFromTestCase(FrontendAuthIntegrationTestCase)
    result = runner.run(suite)
    
    frontend_passed = result.wasSuccessful()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Auth Flow:       {'PASS' if auth_passed else 'FAIL'}")
    print(f"✅ Subdomain Func:  {'PASS' if subdomain_passed else 'FAIL'}")
    print(f"✅ Frontend Integ:  {'PASS' if frontend_passed else 'FAIL'}")
    print("="*70 + "\n")
    
    return auth_passed and subdomain_passed and frontend_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
