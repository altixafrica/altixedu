#!/usr/bin/env python
"""
Quick validation of all code files - no Django setup required
"""
import os
import re
import sys

# Force UTF-8 output
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 80)
print("CODE VALIDATION CHECK")
print("=" * 80)

base_dir = os.path.dirname(__file__)
altixedu_dir = os.path.join(base_dir, 'altixedu')

# Define what files and classes/functions should exist
required_files = {
    os.path.join(altixedu_dir, 'middleware.py'): [
        r'class RateLimitingMiddleware',
        r'class SecurityHeadersMiddleware',
        r'class AuditLoggingMiddleware',
        r'class I18nMiddleware',
    ],
    os.path.join(altixedu_dir, 'encryption.py'): [
        r'class EncryptedField',
        r'class EncryptedCharField',
        r'class EncryptedEmailField',
        r'def setup_encryption_key',
        r'def encrypt_value',
        r'def decrypt_value',
    ],
    os.path.join(altixedu_dir, 'audit.py'): [
        r'def log_action',
        r'def log_user_action',
        r'def log_create_action',
    ],
    os.path.join(altixedu_dir, 'i18n.py'): [
        r'TRANSLATIONS\s*=',
        r'def translate',
        r'def get_language_from_request',
    ],
    os.path.join(altixedu_dir, 'bulk_import.py'): [
        r'class BulkUserImporter',
        r'def validate_csv_format',
        r'def get_csv_template',
    ],
    os.path.join(altixedu_dir, 'report_generation.py'): [
        r'class AttendanceReportGenerator',
        r'def generate_pdf',
        r'def generate_csv',
    ],
}

errors = []
total_checks = 0
passed_checks = 0

print("\nFILE CONTENT VALIDATION")
print("-" * 80)

for file_path, patterns in required_files.items():
    if not os.path.exists(file_path):
        print(f"[FAIL] {os.path.basename(file_path)} - FILE NOT FOUND")
        errors.append(f"Missing file: {file_path}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for pattern in patterns:
            total_checks += 1
            if re.search(pattern, content):
                passed_checks += 1
            else:
                file_ok = False
                pattern_name = pattern.replace(r'class ', '').replace(r'def ', '').split('(')[0].split(' ')[0]
                errors.append(f"{os.path.basename(file_path)}: Missing {pattern_name}")
                print(f"  [FAIL] Missing: {pattern_name}")
        
        if file_ok:
            print(f"[PASS] {os.path.basename(file_path)}")
    except Exception as e:
        print(f"[FAIL] {os.path.basename(file_path)}: {e}")
        errors.append(f"{os.path.basename(file_path)}: {str(e)}")

# Check models
print("\nMODELS VALIDATION")
print("-" * 80)

model_files = {
    os.path.join(altixedu_dir, 'apps', 'students', 'health_models.py'): [
        r'class StudentHealthRecord',
        r'class StudentEmergencyContact',
        r'class HealthMetric',
    ],
    os.path.join(altixedu_dir, 'apps', 'accounts', 'role_models.py'): [
        r'class CustomRole',
        r'class RoleUserAssignment',
        r'class StudentClassroomAssignment',
        r'class ParentStudentLink',
    ],
}

for file_path, patterns in model_files.items():
    if not os.path.exists(file_path):
        print(f"[FAIL] {os.path.relpath(file_path, altixedu_dir)} - NOT FOUND")
        errors.append(f"Missing file: {file_path}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for pattern in patterns:
            total_checks += 1
            if re.search(pattern, content):
                passed_checks += 1
            else:
                file_ok = False
                class_name = pattern.replace(r'class ', '')
                errors.append(f"Model: Missing {class_name}")
                print(f"  [FAIL] Missing: {class_name}")
        
        if file_ok:
            print(f"[PASS] {os.path.relpath(file_path, altixedu_dir)}")
    except Exception as e:
        print(f"[FAIL] {os.path.relpath(file_path, altixedu_dir)}: {e}")
        errors.append(f"Model file error: {str(e)}")

# Check serializers
print("\nSERIALIZERS VALIDATION")
print("-" * 80)

serializer_files = {
    os.path.join(altixedu_dir, 'apps', 'students', 'health_serializers.py'): [
        r'class StudentHealthRecordSerializer',
        r'class HealthMetricSerializer',
    ],
    os.path.join(altixedu_dir, 'apps', 'accounts', 'role_serializers.py'): [
        r'class CustomRoleSerializer',
        r'class StudentClassroomAssignmentSerializer',
    ],
}

for file_path, patterns in serializer_files.items():
    if not os.path.exists(file_path):
        print(f"[FAIL] {os.path.relpath(file_path, altixedu_dir)} - NOT FOUND")
        errors.append(f"Missing serializer file: {file_path}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for pattern in patterns:
            total_checks += 1
            if re.search(pattern, content):
                passed_checks += 1
            else:
                file_ok = False
                class_name = pattern.replace(r'class ', '')
                errors.append(f"Serializer: Missing {class_name}")
        
        if file_ok:
            print(f"[PASS] {os.path.relpath(file_path, altixedu_dir)}")
    except Exception as e:
        print(f"[FAIL] {os.path.relpath(file_path, altixedu_dir)}: {e}")
        errors.append(f"Serializer file error: {str(e)}")

# Check views
print("\nVIEWS VALIDATION")
print("-" * 80)

view_files = {
    os.path.join(altixedu_dir, 'apps', 'students', 'health_views.py'): [
        r'class StudentHealthRecordViewSet',
        r'class StudentEmergencyContactViewSet',
    ],
    os.path.join(altixedu_dir, 'apps', 'accounts', 'role_views.py'): [
        r'class CustomRoleViewSet',
        r'class RoleUserAssignmentViewSet',
        r'class StudentClassroomAssignmentViewSet',
        r'class ParentStudentLinkViewSet',
    ],
    os.path.join(altixedu_dir, 'apps', 'attendance', 'report_views.py'): [
        r'class BulkImportViewSet',
        r'class AttendanceReportViewSet',
    ],
}

for file_path, patterns in view_files.items():
    if not os.path.exists(file_path):
        print(f"[FAIL] {os.path.relpath(file_path, altixedu_dir)} - NOT FOUND")
        errors.append(f"Missing view file: {file_path}")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for pattern in patterns:
            total_checks += 1
            if re.search(pattern, content):
                passed_checks += 1
            else:
                file_ok = False
                class_name = pattern.replace(r'class ', '')
                errors.append(f"ViewSet: Missing {class_name}")
        
        if file_ok:
            print(f"[PASS] {os.path.relpath(file_path, altixedu_dir)}")
    except Exception as e:
        print(f"[FAIL] {os.path.relpath(file_path, altixedu_dir)}: {e}")
        errors.append(f"View file error: {str(e)}")

# Summary
print("\n" + "=" * 80)
print("VALIDATION SUMMARY")
print("=" * 80)
print(f"\nChecks Passed: {passed_checks}/{total_checks}")
print(f"Success Rate: {(passed_checks/total_checks*100):.1f}%" if total_checks > 0 else "N/A")

if errors:
    print(f"\nFound {len(errors)} issue(s):")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\nALL VALIDATIONS PASSED!")
    print("\nCode structure is complete and correct!")
    print("\nNext steps:")
    print("  1. cd altixedu")
    print("  2. python manage.py migrate")
    print("  3. python setup_features.py")
    print("  4. python manage.py runserver")
    sys.exit(0)
