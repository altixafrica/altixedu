#!/bin/bash

# Get admin token
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@atlascollege.test","password":"Password123!"}')

echo "Admin login response:"
echo "$ADMIN_TOKEN" | python -m json.tool
echo ""

TOKEN=$(echo "$ADMIN_TOKEN" | grep -o '"token":"[^"]*' | head -1 | cut -d'"' -f4)
echo "Extracted token: $TOKEN"
echo ""

# Check admin dashboard
echo "=== Admin Dashboard ==="
curl -s -X GET http://127.0.0.1:8000/api/dashboard/schooladmin/ \
  -H "Authorization: Token $TOKEN" | python -m json.tool

echo ""
echo ""

# Get student token
STUDENT_LOGIN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"student@atlascollege.test","password":"Password123!"}')

STUDENT_TOKEN=$(echo "$STUDENT_LOGIN" | grep -o '"token":"[^"]*' | head -1 | cut -d'"' -f4)
echo "Student token: $STUDENT_TOKEN"
echo ""

echo "=== Student Dashboard ==="
curl -s -X GET http://127.0.0.1:8000/api/dashboard/student/ \
  -H "Authorization: Token $STUDENT_TOKEN" | python -m json.tool
