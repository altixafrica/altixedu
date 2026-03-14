# Initial migration for teachers app
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0003_school_subdomain_is_active'),
        ('academics', '0002_exam_examresult'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employment_date', models.DateField(help_text='Date teacher was employed')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('retired', 'Retired'), ('on_leave', 'On Leave')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='schools.school')),
                ('user', models.OneToOneField(blank=True, help_text='Optional linked user account for login', limit_choices_to={'role': 'teacher'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['school', 'user__last_name'],
            },
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['school', 'status'], name='teacher_school_status_idx'),
        ),
        migrations.AddIndex(
            model_name='teacher',
            index=models.Index(fields=['user'], name='teacher_user_idx'),
        ),
    ]
