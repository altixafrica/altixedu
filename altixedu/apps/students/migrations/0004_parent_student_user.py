# Migration for students app - add Parent model and user field
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_remove_student_photo_student_photo_url'),
        ('schools', '0003_school_subdomain_is_active'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add user field to Student
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(blank=True, help_text='Optional linked user account for login', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
        
        # Create Parent model
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, help_text='Parent contact phone number', max_length=20, null=True)),
                ('address', models.TextField(blank=True, help_text='Residential address', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='schools.school')),
                ('user', models.OneToOneField(blank=True, help_text='Optional linked user account for login', limit_choices_to={'role': 'parent'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['school', 'user__last_name'],
            },
        ),
        
        # Add indexes to Parent
        migrations.AddIndex(
            model_name='parent',
            index=models.Index(fields=['school', 'user'], name='parent_school_user_idx'),
        ),
    ]
