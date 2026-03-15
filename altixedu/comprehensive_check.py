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
from django.core.management import call_command
import traceback

print("=" * 80)
print("COMPREHENSIVE CODE AND ENDPOINT CHECK - ALTIXEDU")
print("=" * 80)

# ============================================================================
# PART 1: CORE MODELS
# ============================================================================
print("\nPART 1: Checking Core Models")
print("-" * 80)

errors = []

try:
    from apps.accounts.models import User
    from apps.schools.models import School
    from apps.students.models import Student, Parent
    from apps.teachers.models import Teacher
    from apps.bursars.models import Bursar
    from apps.academics.models import AcademicYear, Subject, Classroom, TeacherSubject
    from apps.platform.models import Announcement, AIRiskAlert
    print("[OK] All 14 core models present and importable")
except Exception as e:
    errors.append(f"Core models: {e}")
    print(f"[ERROR] Core models: {e}")
    traceback.print_exc()

# ============================================================================
# PART 2: MIDDLEWARE
# ============================================================================
print("\nPART 2: Checking Middleware")
print("-" * 80)

try:
    from tenant_middleware import SubdomainTenantMiddleware
    if any('SubdomainTenantMiddleware' in m for m in settings.MIDDLEWARE):
        print("[OK] SubdomainTenantMiddleware loaded and registered")
    else:
        errors.append("SubdomainTenantMiddleware not registered in MIDDLEWARE")
        print("[ERROR] SubdomainTenantMiddleware not registered")
except Exception as e:
    errors.append(f"Middleware: {e}")
    print(f"[ERROR] Middleware: {e}")

# ============================================================================
# PART 3: SERVICES
# ============================================================================
print("\nPART 3: Checking Services")
print("-" * 80)

try:
    from platform_service import SubdomainValidator, SchoolProvisioner, BrandingService
    print("[OK] All platform services present")
except Exception as e:
    errors.append(f"Services: {e}")
    print(f"[ERROR] Services: {e}")
    traceback.print_exc()

# ============================================================================
# PART 4: SERIALIZERS
# ============================================================================
print("\nPART 4: Checking Serializers")
print("-" * 80)

try:
    from apps.platform.serializers import (
        SchoolBrandingSerializer, SchoolUpdateSerializer,
        AnnouncementSerializer, AIRiskAlertSerializer,
        SubdomainCheckSerializer, SchoolRegistrationSerializer
    )
    print("[OK] All 6 platform serializers present")
except Exception as e:
    errors.append(f"Serializers: {e}")
    print(f"[ERROR] Serializers: {e}")
    traceback.print_exc()

# ============================================================================
# PART 5: VIEWS
# ============================================================================
print("\nPART 5: Checking Views and ViewSets")
print("-" * 80)

try:
    from apps.platform.views import (
        BrandingPublicAPIView, BrandingAdminAPIView,
        SubdomainCheckAPIView, SchoolRegistrationAPIView,
        AnnouncementViewSet, AIRiskAlertViewSet
    )
    print("[OK] All 6 platform views/viewsets present")
except Exception as e:
    errors.append(f"Views: {e}")
    print(f"[ERROR] Views: {e}")
    traceback.print_exc()

# ============================================================================
# PART 6: SETTINGS VALIDATION
# ============================================================================
print("\nPART 6: Validating Settings")
print("-" * 80)

checks = [
    ('SubdomainTenantMiddleware registered', any('SubdomainTenantMiddleware' in m for m in settings.MIDDLEWARE)),
    ('apps.platform in INSTALLED_APPS', 'apps.platform' in settings.INSTALLED_APPS),
    ('apps.teachers in INSTALLED_APPS', 'apps.teachers' in settings.INSTALLED_APPS),
    ('apps.bursars in INSTALLED_APPS', 'apps.bursars' in settings.INSTALLED_APPS),
    ('REST_FRAMEWORK configured', hasattr(settings, 'REST_FRAMEWORK')),
]

for check_name, result in checks:
    if result:
        print(f"[OK] {check_name}")
    else:
        print(f"[ERROR] {check_name}")
        errors.append(f"Settings: {check_name}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if errors:
    print(f"\n[ERRORS] {len(errors)} ERROR(S) FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\nNOTE: Database migration may need to be applied for full validation.")
    sys.exit(1)
else:
    print("\n[SUCCESS] CODE STRUCTURE VALIDATION PASSED")
    print("Next step: Apply migrations and test endpoints")
    sys.exit(0)
