"""
Signal handlers for notifications app.
Automatically creates notification preferences for new users.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import User
from apps.notifications.models import NotificationPreference


@receiver(post_save, sender=User)
def create_notification_preference(sender, instance, created, **kwargs):
    """
    Automatically create NotificationPreference when a new User is created.
    """
    if created:
        NotificationPreference.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_notification_preference(sender, instance, **kwargs):
    """
    Ensure NotificationPreference exists for every user.
    This handles cases where a user is updated.
    """
    if hasattr(instance, 'notification_preferences'):
        instance.notification_preferences.save()
