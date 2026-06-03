# Generated migration for NotificationPreference model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0002_alter_studentaiinsights_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_enabled', models.BooleanField(default=True, help_text='Receive email notifications')),
                ('sms_enabled', models.BooleanField(default=False, help_text='Receive SMS notifications')),
                ('in_app_enabled', models.BooleanField(default=True, help_text='Receive in-app notifications')),
                ('announcements_enabled', models.BooleanField(default=True)),
                ('messages_enabled', models.BooleanField(default=True)),
                ('grades_enabled', models.BooleanField(default=True)),
                ('attendance_enabled', models.BooleanField(default=True)),
                ('fees_enabled', models.BooleanField(default=True)),
                ('schedule_enabled', models.BooleanField(default=True)),
                ('system_enabled', models.BooleanField(default=False)),
                ('quiet_hours_start', models.TimeField(blank=True, help_text='Do not send notifications before this time', null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, help_text='Do not send notifications after this time', null=True)),
                ('digest_frequency', models.CharField(choices=[('realtime', 'Real-time'), ('daily', 'Daily Digest'), ('weekly', 'Weekly Digest'), ('never', 'Never')], default='realtime', help_text='How often to receive notification digests', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Notification Preferences',
            },
        ),
    ]
