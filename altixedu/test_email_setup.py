"""
Quick test script to verify email service works
Run with: python manage.py shell < test_email_setup.py
"""

from django.conf import settings
from apps.notifications.notification_service import email_service
from apps.notifications.email_templates import send_welcome_email

# Test 1: Check if email service is configured
print("=" * 60)
print("EMAIL SERVICE SETUP TEST")
print("=" * 60)

email_provider = getattr(settings, 'EMAIL_PROVIDER', 'Not configured')
print(f"\n✓ EMAIL_PROVIDER: {email_provider}")

if email_provider == 'mailgun':
    api_key = getattr(settings, 'MAILGUN_API_KEY', 'Not set')
    domain = getattr(settings, 'MAILGUN_DOMAIN', 'Not set')
    sender = getattr(settings, 'MAILGUN_SENDER_EMAIL', 'Not set')
    
    print(f"✓ MAILGUN_API_KEY: {'*' * 10}{'✓' if api_key != 'Not set' else '✗'}")
    print(f"✓ MAILGUN_DOMAIN: {domain}")
    print(f"✓ MAILGUN_SENDER_EMAIL: {sender}")

print("\n" + "=" * 60)
print("TEST EMAIL SENDING")
print("=" * 60)

# Test 2: Try to send test email
test_email = "test@altixedu.com"
try:
    print(f"\nAttempting to send test email to: {test_email}")
    
    result = email_service.send_email(
        to_email=test_email,
        subject="✓ AltixEdu Email Setup Test",
        body="This is a test email to verify your email configuration is working.",
        html_body="""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>✓ Email Configuration Test</h2>
                <p>Congratulations! Your email service is working correctly.</p>
                <p><strong>Provider:</strong> """ + email_provider + """</p>
                <p>You can now enable email notifications for announcements, payments, and grades.</p>
                <hr>
                <p style="color: #666; font-size: 12px;">© 2026 AltixEdu</p>
            </body>
        </html>
        """
    )
    
    if result:
        print("✓ Test email sent successfully!")
    else:
        print("✗ Failed to send test email. Check your configuration.")
        
except Exception as e:
    print(f"✗ Error sending test email: {str(e)}")

print("\n" + "=" * 60)
print("NOTIFICATION PREFERENCES TEST")
print("=" * 60)

from apps.accounts.models import User
from apps.notifications.models import NotificationPreference

# Test 3: Check if we can create notification preferences
try:
    user = User.objects.first()
    if user:
        prefs, created = NotificationPreference.objects.get_or_create(user=user)
        print(f"\n✓ User: {user.username}")
        print(f"✓ Email notifications enabled: {prefs.email_enabled}")
        print(f"✓ Announcements enabled: {prefs.announcements_enabled}")
        print(f"✓ Messages enabled: {prefs.messages_enabled}")
        print(f"✓ Grades enabled: {prefs.grades_enabled}")
    else:
        print("\n✗ No users found in database")
except Exception as e:
    print(f"\n✗ Error checking notification preferences: {str(e)}")

print("\n" + "=" * 60)
print("SETUP COMPLETE!")
print("=" * 60)
print("\nNext steps:")
print("1. Configure your email provider (Mailgun, Resend, etc.)")
print("2. Set EMAIL_PROVIDER and API keys in .env")
print("3. Test with: python manage.py shell < test_email_setup.py")
print("4. Emails will be sent for announcements, payments, and grades")
print("\nDocumentation: SMS_EMAIL_INTEGRATION_COMPLETE_GUIDE.md")
