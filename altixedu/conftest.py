import os
import django
from django.conf import settings

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')
django.setup()

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def db_transaction(db):
    """
    Fixture for transactional database access.
    """
    return db


@pytest.fixture
def authenticated_user(db):
    """
    Create a test authenticated user.
    """
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def api_client():
    """
    Return Django REST Framework API test client.
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, authenticated_user):
    """
    Return authenticated API test client.
    """
    api_client.force_authenticate(user=authenticated_user)
    return api_client
