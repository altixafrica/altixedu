#!/bin/bash

# Phase 4 Implementation Test Script
# Tests: Ministry Admin Login & School State Collection

BASE_URL="http://localhost:8000"
MINISTRY_EMAIL="ministry_admin@example.com"
MINISTRY_PASSWORD="TestPassword123"
SUPERADMIN_TOKEN="your-superadmin-token-here"

echo "=========================================="
echo "  PHASE 4 ENDPOINT TESTS"
echo "=========================================="
echo ""

# Test 1: Ministry Admin Login
echo "Test 1: Ministry Admin Login Endpoint"
echo "Endpoint: POST /api/auth/login/ministry/"
echo "---"
curl -X POST "$BASE_URL/api/auth/login/ministry/" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$MINISTRY_EMAIL\",
    \"password\": \"$MINISTRY_PASSWORD\"
  }" | python -m json.tool
echo ""
echo "Expected Response: 200 OK with token, user, ministry data (country, state, currency)"
echo ""
echo ""

# Test 2: School Setup - Missing State Field (Should Fail)
echo "Test 2: School Setup WITHOUT State Field (Should Return 400)"
echo "Endpoint: POST /api/schools/setup/"
echo "---"
curl -X POST "$BASE_URL/api/schools/setup/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -d "{
    \"name\": \"Test School\",
    \"subdomain\": \"test-school-1\",
    \"email\": \"test1@school.com\",
    \"phone\": \"08012345678\",
    \"address\": \"123 Main Street\",
    \"city\": \"Lagos\",
    \"country\": \"Nigeria\"
  }" | python -m json.tool
echo ""
echo "Expected Response: 400 Bad Request - Missing required fields: ['state']"
echo ""
echo ""

# Test 3: School Setup - With State Field (Should Succeed)
echo "Test 3: School Setup WITH State Field (Should Return 201)"
echo "Endpoint: POST /api/schools/setup/"
echo "---"
curl -X POST "$BASE_URL/api/schools/setup/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -d "{
    \"name\": \"Test School\",
    \"subdomain\": \"test-school-2\",
    \"email\": \"test2@school.com\",
    \"phone\": \"08012345678\",
    \"address\": \"123 Main Street\",
    \"city\": \"Lagos\",
    \"state\": \"Lagos\",
    \"country\": \"Nigeria\"
  }" | python -m json.tool
echo ""
echo "Expected Response: 201 Created with school data including state confirmation"
echo ""
echo ""

# Test 4: School Setup - Non-Superadmin Cannot Create Schools
echo "Test 4: Non-Superadmin Trying to Create School (Should Return 403)"
echo "Endpoint: POST /api/schools/setup/ (as ministry_admin)"
echo "---"
curl -X POST "$BASE_URL/api/schools/setup/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ministry_admin_token" \
  -d "{
    \"name\": \"Test School\",
    \"subdomain\": \"test-school-3\",
    \"email\": \"test3@school.com\",
    \"phone\": \"08012345678\",
    \"address\": \"123 Main Street\",
    \"city\": \"Lagos\",
    \"state\": \"Lagos\",
    \"country\": \"Nigeria\"
  }" | python -m json.tool
echo ""
echo "Expected Response: 403 Forbidden - Only superadmin, ministry admin, or school admin can create schools"
echo ""
echo ""

# Test 5: Duplicate School Subdomain (Should Fail)
echo "Test 5: Creating School with Duplicate Subdomain (Should Return 400)"
echo "Endpoint: POST /api/schools/setup/"
echo "---"
curl -X POST "$BASE_URL/api/schools/setup/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SUPERADMIN_TOKEN" \
  -d "{
    \"name\": \"Duplicate School\",
    \"subdomain\": \"test-school-2\",
    \"email\": \"duplicate@school.com\",
    \"phone\": \"08012345678\",
    \"address\": \"123 Main Street\",
    \"city\": \"Lagos\",
    \"state\": \"Lagos\",
    \"country\": \"Nigeria\"
  }" | python -m json.tool
echo ""
echo "Expected Response: 400 Bad Request - School with this subdomain already exists"
echo ""

echo ""
echo "=========================================="
echo "  TEST SUITE COMPLETE"
echo "=========================================="
echo ""
echo "To run these tests:"
echo "1. Start the server: cd altixedu && python manage.py runserver"
echo "2. Create a ministry admin user via Django admin or API"
echo "3. Update MINISTRY_EMAIL and MINISTRY_PASSWORD in this script"
echo "4. Run: bash test_phase4_endpoints.sh"
