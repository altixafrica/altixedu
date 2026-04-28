import os
import django
from django.conf import settings

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')

if not settings.configured:
    django.setup()

import pytest
from django.test.utils import get_runner
from django.db import connections
from django.test.db import creation


@pytest.fixture(scope='session')
def django_db_setup():
    """
    Setup Django test database at session level.
    """
    from django.conf import settings
    from django.test.utils import get_runner
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=0, interactive=False, keepdb=True)
    
    # Create test database
    old_config = test_runner.setup_test_environment()
    return old_config


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
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='SecureTest@123'
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
