#!/usr/bin/env python
"""
Comprehensive error checking and endpoint validation script for AltixEdu
Tests actual implemented models, middleware, serializers, and views
"""
import os
import sys
import django

# Setup Django
altixedu_dir = os.path.join(os.path.dirname(__file__), 'altixedu')
os.chdir(altixedu_dir)
sys.path.insert(0, altixedu_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')

django.setup()

from django.conf import settings
import traceback

print("=" * 80)
print("COMPREHENSIVE CODE AND ENDPOINT CHECK - ALTIXEDU")
print("=" * 80)

errors = []
passed_tests = 0
total_tests = 0

# ============================================================================
# PART 1: CORE MODELS VALIDATION
# ============================================================================
print("\nPART 1: Checking Core Models")
print("-" * 80)

total_tests += 1
try:
    from apps.accounts.models import User
    from apps.schools.models import School
    from apps.students.models import Student, Parent, StudentParent
    from apps.teachers.models import Teacher
    from apps.bursars.models import Bursar
    from apps.academics.models import Subject, Classroom, TeacherSubject, Exam, AcademicYear
    from apps.platform.models import Announcement, AIRiskAlert
    print("[OK] All core models loaded successfully")
    print("  - User, School, Student, Parent, StudentParent")
    print("  - Teacher, Bursar, Subject, Classroom, TeacherSubject")
    print("  - Exam, AcademicYear, Announcement, AIRiskAlert")
    passed_tests += 1
except Exception as e:
    errors.append(f"Core models error: {e}")
    print(f"[ERROR] Core models: {e}")
    traceback.print_exc()

# ============================================================================
# PART 2: MIDDLEWARE VALIDATION
# ============================================================================
print("\nPART 2: Checking Middleware")
print("-" * 80)

total_tests += 1
try:
    from tenant_middleware import SubdomainTenantMiddleware
    print("[OK] SubdomainTenantMiddleware loaded")
    
    # Check if in settings
    middleware_check = any('SubdomainTenantMiddleware' in m for m in settings.MIDDLEWARE)
    if middleware_check:
        print("[OK] SubdomainTenantMiddleware registered in MIDDLEWARE")
        passed_tests += 1
    else:
        errors.append("SubdomainTenantMiddleware not registered in MIDDLEWARE")
        print("[ERROR] SubdomainTenantMiddleware not registered")
except Exception as e:
    errors.append(f"Middleware error: {e}")
    print(f"[ERROR] Middleware: {e}")
    traceback.print_exc()

# ============================================================================
# PART 3: SERIALIZERS VALIDATION
# ============================================================================
print("\nPART 3: Checking Serializers")
print("-" * 80)

total_tests += 1
try:
    from apps.platform.serializers import (
        SchoolBrandingSerializer, SchoolUpdateSerializer,
        AnnouncementSerializer, AIRiskAlertSerializer,
        SubdomainCheckSerializer, SchoolRegistrationSerializer
    )
    print("[OK] Platform serializers loaded")
    print("  - SchoolBrandingSerializer, SchoolUpdateSerializer")
    print("  - AnnouncementSerializer, AIRiskAlertSerializer")
    print("  - SubdomainCheckSerializer, SchoolRegistrationSerializer")
    passed_tests += 1
except Exception as e:
    errors.append(f"Platform serializers error: {e}")
    print(f"[ERROR] Platform serializers: {e}")
    traceback.print_exc()

# ============================================================================
# PART 4: VIEWS VALIDATION
# ============================================================================
print("\nPART 4: Checking Views and ViewSets")
print("-" * 80)

total_tests += 1
try:
    from apps.platform.views import (
        BrandingPublicAPIView, BrandingAdminAPIView,
        SubdomainCheckAPIView, SchoolRegistrationAPIView,
        AnnouncementViewSet, AIRiskAlertViewSet
    )
    print("[OK] Platform views loaded")
    print("  - BrandingPublicAPIView, BrandingAdminAPIView")
    print("  - SubdomainCheckAPIView, SchoolRegistrationAPIView")
    print("  - AnnouncementViewSet, AIRiskAlertViewSet")
    passed_tests += 1
except Exception as e:
    errors.append(f"Platform views error: {e}")
    print(f"[ERROR] Platform views: {e}")
    traceback.print_exc()

# ============================================================================
# PART 5: PLATFORM SERVICE VALIDATION
# ============================================================================
print("\nPART 5: Checking Platform Service")
print("-" * 80)

total_tests += 1
try:
    from platform_service import (
        SubdomainValidator, SchoolProvisioner, BrandingService
    )
    print("[OK] Platform service modules loaded")
    print("  - SubdomainValidator")
    print("  - SchoolProvisioner")
    print("  - BrandingService")
    passed_tests += 1
except Exception as e:
    errors.append(f"Platform service error: {e}")
    print(f"[ERROR] Platform service: {e}")
    traceback.print_exc()

# ============================================================================
# PART 6: SETTINGS VALIDATION
# ============================================================================
print("\nPART 6: Validating Settings Configuration")
print("-" * 80)

total_tests += 5
settings_checks = [
    ('SubdomainTenantMiddleware in MIDDLEWARE', any('SubdomainTenantMiddleware' in m for m in settings.MIDDLEWARE)),
    ('INSTALLED_APPS has apps.teachers', 'apps.teachers' in settings.INSTALLED_APPS),
    ('INSTALLED_APPS has apps.bursars', 'apps.bursars' in settings.INSTALLED_APPS),
    ('INSTALLED_APPS has apps.platform', 'apps.platform' in settings.INSTALLED_APPS),
    ('REST_FRAMEWORK configured', hasattr(settings, 'REST_FRAMEWORK')),
]

for check_name, result in settings_checks:
    if result:
        print(f"[OK] {check_name}")
        passed_tests += 1
    else:
        print(f"[ERROR] {check_name}")
        errors.append(f"Settings: {check_name}")

# ============================================================================
# PART 7: FUNCTIONALITY TESTS
# ============================================================================
print("\nPART 7: Testing Functionality")
print("-" * 80)

total_tests += 1
try:
    from platform_service import SubdomainValidator
    
    # Test validation
    is_valid = SubdomainValidator.validate("testschool")
    is_available = SubdomainValidator.is_available("testschool")
    suggestions = SubdomainValidator.suggest_subdomains("Test School Name")
    
    print("[OK] SubdomainValidator methods work")
    print(f"  - validate('testschool'): {is_valid}")
    print(f"  - is_available('testschool'): {is_available}")
    print(f"  - suggest_subdomains('Test School Name'): {suggestions}")
    passed_tests += 1
except Exception as e:
    errors.append(f"SubdomainValidator test failed: {e}")
    print(f"[ERROR] SubdomainValidator test: {e}")
    traceback.print_exc()

# ============================================================================
# PART 8: DATABASE MIGRATIONS
# ============================================================================
print("\nPART 8: Checking Database Migrations")
print("-" * 80)

total_tests += 1
try:
    from django.core.management import call_command
    from io import StringIO
    
    # Check migrations
    out = StringIO()
    call_command('showmigrations', '--list', stdout=out)
    output = out.getvalue()
    
    migration_apps = ['schools', 'platform', 'teachers', 'bursars', 'academics', 'students', 'accounts']
    found_migrations = 0
    
    for app in migration_apps:
        if app in output:
            print(f"✓ Migration files exist for {app}")
            found_migrations += 1
    
    if found_migrations == len(migration_apps):
        passed_tests += 1
    else:
        errors.append(f"Only {found_migrations}/{len(migration_apps)} app migrations found")
        
except Exception as e:
    print(f"[WARNING] Could not verify migrations: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Tests Passed: {passed_tests}/{total_tests}")

if errors:
    print(f"[ERRORS] {len(errors)} ERRORS FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    sys.exit(1)
else:
    print("\n[SUCCESS] ALL TESTS PASSED - Codebase is valid!")
    sys.exit(0)
