# Initial migration for bursars app
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0003_school_subdomain_is_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bursar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('managed_fees', models.JSONField(blank=True, default=dict, help_text='Fee structure and payment details', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bursars', to='schools.school')),
                ('user', models.OneToOneField(blank=True, help_text='Optional linked user account for login', limit_choices_to={'role': 'bursar'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bursar_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['school'],
            },
        ),
        migrations.AddIndex(
            model_name='bursar',
            index=models.Index(fields=['school'], name='bursar_school_idx'),
        ),
        migrations.AddIndex(
            model_name='bursar',
            index=models.Index(fields=['user'], name='bursar_user_idx'),
        ),
    ]
