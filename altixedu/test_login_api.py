#!/usr/bin/env python
"""
Test script for login API endpoint
"""
import os
import django
import sys
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
sys.path.insert(0, '/c/Users/pc/Documents/altixedu-backend/altixedu')
django.setup()

from django.test import Client

# Create test client
client = Client()

# Test login endpoint
response = client.post(
    '/api/auth/login/',
    data=json.dumps({
        'email': 'admin@atlascollege.test',
        'password': 'Password123!'
    }),
    content_type='application/json'
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"Response: {response.json()}")

# Check if token is returned
if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Login successful!")
    print(f"Token: {data.get('token', 'NO TOKEN')}")
    print(f"User: {data.get('user', {}).get('email')}")
    print(f"Role: {data.get('role')}")
else:
    print(f"\n❌ Login failed!")
    print(f"Response: {response.json()}")
