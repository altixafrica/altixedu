#!/usr/bin/env python
"""
Quick Setup Script - Create Sample Ministry Admin Users
Run this after migrations to set up test/demo ministry admins
"""

import os
import sys
import django

# Add altixedu directory to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'altixedu'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
django.setup()

from apps.accounts.models import User  # type: ignore
from apps.schools.models import Ministry  # type: ignore
from rest_framework.authtoken.models import Token

def create_ministry_admins():
    """Create sample ministry admins for demonstration."""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║   SETUP MINISTRY ADMINS - Demo Data Creation                      ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Define ministry admins to create
    admins_to_create = [
        {
            'email': 'lagos.admin@education.gov.ng',
            'first_name': 'Adekunle',
            'last_name': 'Okafor',
            'password': 'Lagos@2026',
            'country': 'Nigeria',
            'state_or_province': 'Lagos',
        },
        {
            'email': 'kano.admin@education.gov.ng',
            'first_name': 'Amina',
            'last_name': 'Hassan',
            'password': 'Kano@2026',
            'country': 'Nigeria',
            'state_or_province': 'Kano',
        },
        {
            'email': 'nairobi.admin@education.go.ke',
            'first_name': 'James',
            'last_name': 'Kimani',
            'password': 'Nairobi@2026',
            'country': 'Kenya',
            'state_or_province': 'Nairobi',
        },
        {
            'email': 'accra.admin@education.gov.gh',
            'first_name': 'Kwesi',
            'last_name': 'Appiah',
            'password': 'Accra@2026',
            'country': 'Ghana',
            'state_or_province': 'Greater Accra',
        },
    ]
    
    print("\n🏛️  Creating Ministry Admin Users...\n")
    
    for admin in admins_to_create:
        # Check if ministry exists
        try:
            ministry = Ministry.objects.get(
                country=admin['country'],
                state_or_province=admin['state_or_province']
            )
        except Ministry.DoesNotExist:
            print(f"   ⚠️  Ministry not found: {admin['state_or_province']}, {admin['country']}")
            print(f"       Skip creating admin for {admin['email']}")
            continue
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=admin['email'],
            defaults={
                'username': admin['email'].split('@')[0],
                'first_name': admin['first_name'],
                'last_name': admin['last_name'],
                'role': 'ministry_admin',
                'ministry': ministry,
                'is_active': True,
                'is_staff': False,
            }
        )
        
        if created:
            # Set password for new user
            user.set_password(admin['password'])
            user.save()
            
            # Create token
            token, _ = Token.objects.get_or_create(user=user)
            
            print(f"   ✅ Created: {user.get_full_name()}")
            print(f"      📧 Email: {user.email}")
            print(f"      🏛️  Ministry: {ministry.name}")
            print(f"      💱 Currency: {ministry.currency_code}")
            print(f"      🔑 Token: {token.key[:30]}...")
            print(f"      🔐 Password: {admin['password']}")
            print()
        else:
            print(f"   ○ Already exists: {user.email}")
            print()
    
    print("="*70)
    print("✅ Ministry Admin Setup Complete!")
    print("="*70)
    print("""
🎯 NEXT STEPS:

1. Test Login:
   POST /api/auth/login/
   - email: lagos.admin@education.gov.ng
   - password: Lagos@2026

2. Create More Admins:
   POST /api/auth/create-ministry-admin/
   - Use super admin token
   - Specify country and state_or_province

3. Reset Password:
   POST /api/auth/reset-password/
   - For self-reset: include old_password
   - For admin reset: set is_admin_reset: true

4. Access Dashboard:
   GET /api/auth/me/
   - Will show ministry and state-specific permissions
   - All data automatically filtered by state

📊 MINISTRY ADMIN TOUR:

   Each ministry admin can:
   ✓ View all schools in their state
   ✓ See all students in their state
   ✓ Monitor fees and payments
   ✓ Manage approval workflows
   ✓ Export state-specific reports
   ✓ View audit logs
   ✓ Access government features

🔐 SECURITY:

   ✓ State-based data isolation (automatic)
   ✓ Role-based permissions
   ✓ Token-based authentication
   ✓ Password hashing (PBKDF2)
   ✓ Token invalidation on password reset
   ✓ Audit logging (planned)

    """)


if __name__ == '__main__':
    create_ministry_admins()
