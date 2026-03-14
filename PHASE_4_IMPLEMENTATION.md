# Phase 4 Implementation: Separate Ministry Login & School State Collection

**Status:** ✅ COMPLETE - All code implemented and integrated

**Date:** March 13, 2026  
**Phase:** 4 (Final Frontend Requirements)

---

## Overview

Phase 4 implements two critical features as requested:
1. **Separate Ministry Admin Login Endpoint** - Returns ministry-specific context (country, state, currency)
2. **School Setup Endpoint with Mandatory State Collection** - Enforces state field during school creation

---

## Changes Made

### 1. Added MinistryAdminLoginSerializer (serializers.py)

**Purpose:** Handles ministry admin authentication and returns ministry-specific response

**Location:** `altixedu/apps/accounts/serializers.py` (after line 165)

**Key Features:**
- ✅ Validates email + password for ministry_admin role only
- ✅ Returns token (for authentication)
- ✅ Returns user data (id, username, email, name)
- ✅ Returns ministry data (name, country, state_or_province, currency_code, currency_symbol)
- ✅ Returns success message with user's full name

**Code Size:** ~50 lines

**Example Request:**
```json
POST /api/auth/login/ministry/
{
  "email": "ministry_admin@example.com",
  "password": "password123"
}
```

**Example Response (200 OK):**
```json
{
  "token": "abc123token456...",
  "user": {
    "id": 1,
    "username": "ministry_admin",
    "email": "ministry_admin@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe"
  },
  "role": "ministry_admin",
  "ministry": {
    "id": 1,
    "name": "Ministry of Education",
    "country": "Nigeria",
    "state_or_province": "Lagos",
    "currency_code": "NGN",
    "currency_symbol": "₦"
  },
  "message": "Welcome John Doe - Ministry Admin Login Successful"
}
```

---

### 2. Added MinistryAdminLoginView (views.py)

**Purpose:** Separate API endpoint for ministry admin authentication

**Location:** `altixedu/apps/accounts/views.py` (after PasswordResetView, line 579)

**Key Features:**
- ✅ Separate endpoint from general login
- ✅ Allows unauthenticated access (permission_classes = [AllowAny])
- ✅ Uses MinistryAdminLoginSerializer for validation
- ✅ Returns 400 status for invalid credentials
- ✅ Returns 200 status for successful login

**Code Size:** ~12 lines

**Endpoint:**
```
POST /api/auth/login/ministry/
```

---

### 3. Added SchoolSetupView (views.py)

**Purpose:** Enforces state collection during school creation with role-based access control

**Location:** `altixedu/apps/accounts/views.py` (after MinistryAdminLoginView)

**Key Features:**
- ✅ **Requires Authentication** (IsAuthenticated permission)
- ✅ **Role-Based Access Control:**
  - **Superadmin:** Can create schools anywhere
  - **Ministry Admin:** Can create schools only in their assigned state_or_province
  - **School Admin (role='admin'):** 403 Forbidden
  - **Other roles:** 403 Forbidden
- ✅ **Mandatory Fields Validation:**
  - name, subdomain, email, phone, address, city, **state**, country
  - Returns 400 if any required field missing
- ✅ **Uniqueness Validation:**
  - Prevents duplicate subdomains (400 error)
  - Prevents duplicate school emails (400 error)
- ✅ **State Enforcement:**
  - state field is REQUIRED (not optional)
  - state is stored in school.state field
  - state is confirmed in response message
- ✅ **Optional Fields with Defaults:**
  - postal_code (default: '')
  - website (default: '')
  - timezone (default: 'UTC')
  - language (default: 'en')
- ✅ **Error Handling:**
  - 400: Missing required fields
  - 400: Duplicate subdomain
  - 400: Duplicate email
  - 403: Insufficient permissions
  - 500: Server error during school creation
- ✅ **Success Response:**
  - 201 Created with full school data
  - Includes confirmation message with state

**Code Size:** ~120 lines

**Endpoint:**
```
POST /api/schools/setup/
```

**Required Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Example Request:**
```json
{
  "name": "Lagos State International School",
  "subdomain": "lsis-school-1",
  "email": "admin@lsis.com",
  "phone": "08012345678",
  "address": "123 Ikoyi Road, Lagos",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "postal_code": "101234",
  "website": "www.lsis.com",
  "timezone": "UTC+1",
  "language": "en"
}
```

**Example Response (201 Created):**
```json
{
  "id": 1,
  "name": "Lagos State International School",
  "subdomain": "lsis-school-1",
  "email": "admin@lsis.com",
  "phone": "08012345678",
  "address": "123 Ikoyi Road, Lagos",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "website": "www.lsis.com",
  "timezone": "UTC+1",
  "language": "en",
  "message": "School \"Lagos State International School\" created successfully with state \"Lagos\""
}
```

**Error Example (400 - Missing State):**
```json
{
  "error": "Missing required fields: ['state']"
}
```

**Error Example (403 - Non-Superadmin):**
```json
{
  "error": "Only superadmin, ministry admin, or school admin can create schools"
}
```

**Error Example (403 - Wrong State):**
```json
{
  "error": "Ministry admin can only create schools in Lagos"
}
```

---

### 4. Updated Imports in views.py

**Added:**
- `MinistryAdminLoginSerializer` to serializers import
- `School` model from apps.schools.models

**Location:** Line 9 (MinistryAdminLoginSerializer) and Line 16 (School model)

---

### 5. Updated Imports in urls.py

**Added to accounts.views import:**
- `MinistryAdminLoginView`
- `SchoolSetupView`

**Location:** Lines 35-36

---

### 6. Added URL Routes in urls.py

**New Routes Added:**
```python
path('api/auth/login/ministry/', MinistryAdminLoginView.as_view(), name='ministry-login'),
path('api/schools/setup/', SchoolSetupView.as_view(), name='school-setup'),
```

**Location:** After reset-password route (lines 76-77)

---

## API Endpoint Summary

| Endpoint | Method | Purpose | Auth | State Handling |
|----------|--------|---------|------|---|
| `/api/auth/login/` | POST | General login (all roles) | ❌ | N/A |
| `/api/auth/login/ministry/` | POST | **NEW:** Ministry admin login | ❌ | Returns state_or_province |
| `/api/auth/create-ministry-admin/` | POST | Create ministry admin user | ❌ | Superadmin only |
| `/api/auth/reset-password/` | POST | Password reset | ✅ | N/A |
| `/api/schools/setup/` | POST | **NEW:** Create school with state | ✅ | **ENFORCED: Required** |

---

## Technical Details

### Role-Based School Creation Logic

```
User Role → Permission Check → State Check (if ministry_admin)
├─ superadmin ──→ ✅ Can create in any state → (no state check)
├─ ministry_admin ──→ ✅ Can create in own state → (request.state == user.ministry.state_or_province)
├─ admin (school) ──→ ❌ 403 Forbidden
└─ other roles ──→ ❌ 403 Forbidden
```

### State Field Handling

**Before Phase 4:**
- School model had `state` field (CharField, nullable, blank=True)
- Field was optional during creation
- No validation or requirement

**After Phase 4:**
- School model unchanged (no migrations needed)
- `state` field is now **REQUIRED** in SchoolSetupView
- Validation ensures `state` is not empty
- state is confirmed in success response
- state enables future state-based filtering and access control

---

## Files Modified

| File | Type | Lines | Changes |
|------|------|-------|---------|
| altixedu/apps/accounts/serializers.py | Code | +50 | Added MinistryAdminLoginSerializer |
| altixedu/apps/accounts/views.py | Code | +132 | Added MinistryAdminLoginView, SchoolSetupView, imports |
| altixedu/altixedu/urls.py | Code | +2 | Added 2 URL routes and updated imports |

**Total New Code: ~184 lines**

---

## Testing

### Unit Tests To Implement

```python
# Test MinistryAdminLoginView
def test_ministry_admin_login_success():
    # Should return 200 with token and ministry data
    pass

def test_ministry_admin_login_invalid_credentials():
    # Should return 400 "Ministry admin with this email not found"
    pass

# Test SchoolSetupView
def test_school_setup_success():
    # Should return 201 with school data including state
    pass

def test_school_setup_missing_state():
    # Should return 400 "Missing required fields: ['state']"
    pass

def test_school_setup_duplicate_subdomain():
    # Should return 400 "School with this subdomain already exists"
    pass

def test_school_setup_ministry_admin_wrong_state():
    # Should return 403 "Ministry admin can only create schools in Lagos"
    pass

def test_school_setup_non_superadmin():
    # Should return 403 "Only superadmin... can create schools"
    pass
```

### Manual Integration Tests

See `test_phase4_endpoints.sh` for runnable curl commands

---

## Verification Checklist

- ✅ MinistryAdminLoginSerializer added
- ✅ MinistryAdminLoginView implemented
- ✅ SchoolSetupView implemented with role-based access
- ✅ State field enforced in SchoolSetupView
- ✅ Imports updated in views.py
- ✅ Imports updated in urls.py
- ✅ URL routes added to urlpatterns
- ✅ Code follows Django REST Framework conventions
- ✅ Error handling implemented for all scenarios
- ✅ Role-based permissions checked
- ✅ Unique field validation (subdomain, email)
- ✅ State-based ministry admin restrictions
- ✅ Success messages confirm state storage

---

## Next Steps (Optional, Post-Phase 4)

1. **State-Based Filtering:** Implement queries to filter schools/users by state
2. **Ministry Admin Dashboard:** Add state-level analytics and reporting
3. **State Transfer Logic:** Handle schools crossing state boundaries
4. **Bulk School Import:** CSV import with state validation
5. **Automated Testing:** Implement pytest test suite for all endpoints

---

## Known Limitations & Design Decisions

1. **SchoolSetupView in accounts app:** Could be moved to schools app in future refactoring
2. **No subdomain format validation:** Currently checks only uniqueness, not format (could add regex)
3. **State field naming:** Ministry uses `state_or_province`, School uses `state` (unified in future if desired)
4. **No state creation:** State must exist in Ministry before school creation (could add validation)
5. **Timezone handling:** Default is 'UTC', could auto-set based on country/state

---

## Compliance with Requirements

**Requirement 1:** "make sure for ministry there is a different login point" ✅
- New endpoint: `POST /api/auth/login/ministry/`
- Separate from general login
- Returns ministry-specific data (country, state, currency)

**Requirement 2:** "make sure during school setup to collect state so it data can be stored" ✅
- New endpoint: `POST /api/schools/setup/`
- State field is REQUIRED (enforced with validation)
- state is stored in School.state field
- state is confirmed in response message

---

## Code Quality

- ✅ Follows Django REST Framework best practices
- ✅ Proper error handling with HTTP status codes
- ✅ Clear docstrings and comments
- ✅ Consistent with existing codebase style
- ✅ No breaking changes to existing endpoints
- ✅ No database migrations required
- ✅ Backward compatible

---

**Implementation Complete** ✅ `2026-03-13`
