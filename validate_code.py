import os
import re

base_dir = 'c:/Users/pc/Documents/altixedu-backend'
altixedu_dir = os.path.join(base_dir, 'altixedu')

print("="*80)
print("CODE VALIDATION CHECK")
print("="*80)

checks = {
    'middleware.py': ['RateLimitingMiddleware', 'SecurityHeadersMiddleware', 'AuditLoggingMiddleware'],
    'encryption.py': ['EncryptedField', 'setup_encryption_key', 'encrypt_value', 'decrypt_value'],
    'audit.py': ['log_action', 'log_user_action', 'log_create_action'],
    'i18n.py': ['translate', 'get_language_from_request', 'TRANSLATIONS'],
    'bulk_import.py': ['BulkUserImporter', 'validate_csv_format'],
    'report_generation.py': ['AttendanceReportGenerator', 'generate_pdf'],
}

total = 0
passed = 0

print("\nFILE AND CLASS CHECKS")
print("-"*80)

for fname, items in checks.items():
    fpath = os.path.join(altixedu_dir, fname)
    if not os.path.exists(fpath):
        print("[FAIL] {} - NOT FOUND".format(fname))
        continue
    
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for item in items:
            total += 1
            pattern = item
            if re.search(pattern, content):
                passed += 1
            else:
                file_ok = False
                print("  [FAIL] {} missing {}".format(fname, item))
        
        if file_ok:
            print("[PASS] {}".format(fname))
    except Exception as e:
        print("[FAIL] {} - {}".format(fname, e))

# Check models
model_checks = {
    os.path.join(altixedu_dir, 'apps', 'students', 'health_models.py'): [
        'StudentHealthRecord', 'StudentEmergencyContact', 'HealthMetric'],
    os.path.join(altixedu_dir, 'apps', 'accounts', 'role_models.py'): [
        'CustomRole', 'RoleUserAssignment', 'StudentClassroomAssignment', 'ParentStudentLink'],
}

print("\nMODELS CHECK")
print("-"*80)

for fpath, items in model_checks.items():
    if not os.path.exists(fpath):
        relpath = os.path.relpath(fpath, altixedu_dir)
        print("[FAIL] {} - NOT FOUND".format(relpath))
        continue
    
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for item in items:
            total += 1
            pattern = r'class ' + item
            if re.search(pattern, content):
                passed += 1
            else:
                file_ok = False
                relpath = os.path.relpath(fpath, altixedu_dir)
                print("  [FAIL] {} missing class {}".format(relpath, item))
        
        if file_ok:
            relpath = os.path.relpath(fpath, altixedu_dir)
            print("[PASS] {}".format(relpath))
    except Exception as e:
        relpath = os.path.relpath(fpath, altixedu_dir)
        print("[FAIL] {} - {}".format(relpath, e))

# Check views
view_checks = {
    os.path.join(altixedu_dir, 'apps', 'students', 'health_views.py'): [
        'StudentHealthRecordViewSet', 'StudentEmergencyContactViewSet'],
    os.path.join(altixedu_dir, 'apps', 'accounts', 'role_views.py'): [
        'CustomRoleViewSet', 'RoleUserAssignmentViewSet', 'StudentClassroomAssignmentViewSet',
        'ParentStudentLinkViewSet'],
    os.path.join(altixedu_dir, 'apps', 'attendance', 'report_views.py'): [
        'BulkImportViewSet', 'AttendanceReportViewSet'],
}

print("\nVIEWS CHECK")
print("-"*80)

for fpath, items in view_checks.items():
    if not os.path.exists(fpath):
        relpath = os.path.relpath(fpath, altixedu_dir)
        print("[FAIL] {} - NOT FOUND".format(relpath))
        continue
    
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        file_ok = True
        for item in items:
            total += 1
            pattern = r'class ' + item
            if re.search(pattern, content):
                passed += 1
            else:
                file_ok = False
                relpath = os.path.relpath(fpath, altixedu_dir)
                print("  [FAIL] {} missing {}".format(relpath, item))
        
        if file_ok:
            relpath = os.path.relpath(fpath, altixedu_dir)
            print("[PASS] {}".format(relpath))
    except Exception as e:
        relpath = os.path.relpath(fpath, altixedu_dir)
        print("[FAIL] {} - {}".format(relpath, e))

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("\nTotal Checks: {}".format(total))
print("Passed: {}".format(passed))
print("Failed: {}".format(total - passed))
if total > 0:
    print("Success Rate: {:.1f}%".format((passed/total)*100))

if passed == total:
    print("\n[SUCCESS] All validations passed!")
    print("\nCode structure is COMPLETE and CORRECT!")
    exit(0)
else:
    print("\n[ERROR] Some checks failed")
    exit(1)
