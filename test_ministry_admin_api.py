#!/usr/bin/env python
"""
Test script for Ministry Admin creation and password reset APIs
"""

import os
import sys
import django

# Setup Django
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'altixedu'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
django.setup()

from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.accounts.models import User  # type: ignore
from apps.schools.models import Ministry, School  # type: ignore

def setup_test_data():
    """Create necessary test data."""
    print("\n📋 Setting up test data...")
    
    # Create a superuser if doesn't exist
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@altixedu.com',
            password='Admin@123456',
            role='superadmin'
        )
        print(f"   ✅ Created superuser: admin")
    else:
        admin = User.objects.get(username='admin')
        print(f"   ○ Superuser already exists: admin")
    
    # Create superadmin group
    superadmin_group, _ = Group.objects.get_or_create(name='superadmin')
    admin.groups.add(superadmin_group)
    admin.save()
    
    # Create ministries for testing
    ministries = [
        {
            'name': 'Lagos State Ministry of Education',
            'country': 'Nigeria',
            'state_or_province': 'Lagos',
            'contact_email': 'contact@lagoseducation.gov.ng',
            'contact_phone': '+234-800-0000-001',
            'address': '123 Government Road, Lagos, Nigeria',
            'currency_code': 'NGN',
            'currency_symbol': '₦',
            'state': 'Lagos'  # Legacy field
        },
        {
            'name': 'Kenya Ministry of Education',
            'country': 'Kenya',
            'state_or_province': 'Nairobi',
            'contact_email': 'contact@kenyaeducation.go.ke',
            'contact_phone': '+254-20-0000-001',
            'address': '123 Government Avenue, Nairobi, Kenya',
            'currency_code': 'KES',
            'currency_symbol': 'KES',
            'state': 'Nairobi'  # Legacy field
        },
        {
            'name': 'Ghana Ministry of Education',
            'country': 'Ghana',
            'state_or_province': 'Greater Accra',
            'contact_email': 'contact@ghanaeducation.gov.gh',
            'contact_phone': '+233-30-0000-001',
            'address': '123 Government Street, Accra, Ghana',
            'currency_code': 'GHS',
            'currency_symbol': 'GHS',
            'state': 'Greater Accra'  # Legacy field
        }
    ]
    
    for ministry_data in ministries:
        ministry, created = Ministry.objects.get_or_create(
            country=ministry_data['country'],
            state_or_province=ministry_data['state_or_province'],
            defaults=ministry_data
        )
        status = "✅ Created" if created else "○ Exists"
        print(f"   {status}: {ministry.name}")
    
    print("✅ Test data setup complete!")
    return admin


def test_create_ministry_admin(admin):
    """Test creating a ministry admin."""
    print("\n🧪 Testing Ministry Admin Creation...")
    
    client = APIClient()
    
    # Get admin token
    admin_token = Token.objects.get(user=admin)
    client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
    
    # Test 1: Create Lagos Ministry Admin
    print("   📝 Test 1: Creating Lagos Ministry Admin...")
    response = client.post('/api/auth/create-ministry-admin/', {
        'email': 'adekunle.okafor@lagos.gov.ng',
        'first_name': 'Adekunle',
        'last_name': 'Okafor',
        'password': 'SecurePass@123',
        'country': 'Nigeria',
        'state_or_province': 'Lagos'
    }, format='json')
    
    if response.status_code == 201:
        data = response.json()
        print(f"      ✅ Status: {response.status_code} Created")
        print(f"      📦 Token: {data['token'][:20]}...")
        print(f"      👤 User: {data['user']['full_name']} ({data['user']['email']})")
        print(f"      🏛️  Ministry: {data['ministry']['name']}")
        print(f"      💱 Currency: {data['ministry']['currency_code']}")
        return data
    else:
        print(f"      ❌ Status: {response.status_code}")
        print(f"      📋 Response: {response.json()}")
        return None
    
    
def test_create_ministry_admin_different_countries(admin):
    """Test creating ministry admins for different countries."""
    print("\n   📝 Test 2: Creating Ministry Admins for Different Countries...")
    
    client = APIClient()
    admin_token = Token.objects.get(user=admin)
    client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
    
    test_cases = [
        {
            'data': {
                'email': 'kenya.admin@education.go.ke',
                'first_name': 'Kofi',
                'last_name': 'Mensah',
                'password': 'KenyaSecure@456',
                'country': 'Kenya',
                'state_or_province': 'Nairobi'
            },
            'name': 'Kenya Education Admin'
        },
        {
            'data': {
                'email': 'ghana.admin@education.gov.gh',
                'first_name': 'Kwesi',
                'last_name': 'Appiah',
                'password': 'GhanaSecure@789',
                'country': 'Ghana',
                'state_or_province': 'Greater Accra'
            },
            'name': 'Ghana Education Admin'
        }
    ]
    
    for test in test_cases:
        response = client.post('/api/auth/create-ministry-admin/', test['data'], format='json')
        if response.status_code == 201:
            data = response.json()
            print(f"      ✅ {test['name']}: {data['user']['full_name']}")
            print(f"         Currency: {data['ministry']['currency_code']}")
        else:
            print(f"      ❌ {test['name']}: {response.status_code} - {response.json()}")


def test_password_reset(admin, ministry_admin_data):
    """Test password reset for ministry admin."""
    print("\n🔐 Testing Password Reset...")
    
    client = APIClient()
    
    # Test 1: Ministry Admin resets own password
    print("   📝 Test 1: Ministry Admin resets own password...")
    
    # Get ministry admin token
    ministry_admin_email = ministry_admin_data['user']['email']
    ministry_admin_user = User.objects.get(email=ministry_admin_email)
    ministry_token = Token.objects.get(user=ministry_admin_user)
    
    client.credentials(HTTP_AUTHORIZATION=f'Token {ministry_token.key}')
    
    response = client.post('/api/auth/reset-password/', {
        'email': ministry_admin_email,
        'old_password': 'SecurePass@123',
        'new_password': 'NewSecurePass@456',
        'is_admin_reset': False
    }, format='json')
    
    if response.status_code == 200:
        print(f"      ✅ Status: {response.status_code} OK")
        print(f"      ℹ️  {response.json()['message']}")
    else:
        print(f"      ❌ Status: {response.status_code}")
        print(f"      📋 Response: {response.json()}")
    
    # Test 2: Super Admin forces password reset
    print("\n   📝 Test 2: Super Admin forces password reset...")
    
    admin_token = Token.objects.get(user=admin)
    client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
    
    response = client.post('/api/auth/reset-password/', {
        'email': ministry_admin_email,
        'new_password': 'ForcedReset@789',
        'is_admin_reset': True
    }, format='json')
    
    if response.status_code == 200:
        print(f"      ✅ Status: {response.status_code} OK")
        print(f"      ℹ️  {response.json()['message']}")
    else:
        print(f"      ❌ Status: {response.status_code}")
        print(f"      📋 Response: {response.json()}")


def test_ministry_admin_login():
    """Test ministry admin login."""
    print("\n🔑 Testing Ministry Admin Login...")
    
    client = APIClient()
    
    # Try to login with new password
    email = 'adekunle.okafor@lagos.gov.ng'
    password = 'ForcedReset@789'  # Use the last reset password
    
    response = client.post('/api/auth/login/', {
        'email': email,
        'password': password
    }, format='json')
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Login successful")
        print(f"      👤 User: {data['user']['full_name']}")
        print(f"      🎭 Role: {data['role']}")
        print(f"      📦 Token: {data['token'][:20]}...")
        if 'ministry' in data:
            print(f"      🏛️  Ministry: {data['ministry']['name']}")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        print(f"      Response: {response.json()}")


def main():
    """Run all tests."""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║   MINISTRY ADMIN API - FUNCTIONAL TESTS                           ║
║   Testing: Create Ministry Admin, Password Reset, Login           ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Setup
        admin = setup_test_data()
        
        # Tests
        ministry_admin_data = test_create_ministry_admin(admin)
        if ministry_admin_data:
            test_create_ministry_admin_different_countries(admin)
            test_password_reset(admin, ministry_admin_data)
            test_ministry_admin_login()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70)
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
