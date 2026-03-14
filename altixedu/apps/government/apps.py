"""
Django App Configuration for Government Features
"""

from django.apps import AppConfig


class GovernmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.government'
    verbose_name = 'Government & Compliance Features'
    
    def ready(self):
        """Initialize app."""
        # Import signals here if needed
        # from . import signals
        pass
