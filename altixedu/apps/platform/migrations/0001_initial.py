# Initial migrations for platform app (Announcement and AIRiskAlert models)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0002_ministry'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('students', '0003_remove_student_photo_student_photo_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Announcement title', max_length=255)),
                ('message', models.TextField(help_text='Full announcement message')),
                ('target_role', models.CharField(choices=[('all', 'All Users'), ('students', 'Students Only'), ('teachers', 'Teachers Only'), ('parents', 'Parents Only'), ('admin', 'Admin Only')], default='all', help_text='Who should see this announcement', max_length=20)),
                ('is_pinned', models.BooleanField(default=False, help_text='Pin announcement to top of feed')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='announcements_created', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='schools.school')),
            ],
            options={
                'ordering': ['-is_pinned', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIRiskAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(choices=[('attendance', 'Attendance'), ('grades', 'Grades/Performance'), ('assignment', 'Assignment/Homework'), ('behavior', 'Behavior'), ('health', 'Health'), ('other', 'Other')], help_text='Type of alert', max_length=50)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], help_text='Severity level', max_length=20)),
                ('message', models.TextField(help_text='Alert message')),
                ('recommendation', models.TextField(blank=True, help_text='Recommended action', null=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_risk_alerts', to='schools.school')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='risk_alerts', to='students.student')),
            ],
            options={
                'ordering': ['-severity', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='announcement',
            index=models.Index(fields=['school', '-created_at'], name='ann_school_created_idx'),
        ),
        migrations.AddIndex(
            model_name='announcement',
            index=models.Index(fields=['school', 'target_role'], name='ann_school_role_idx'),
        ),
        migrations.AddIndex(
            model_name='airiskalert',
            index=models.Index(fields=['school', 'student', '-created_at'], name='air_school_student_idx'),
        ),
        migrations.AddIndex(
            model_name='airiskalert',
            index=models.Index(fields=['school', 'severity', 'is_resolved'], name='air_school_severity_idx'),
        ),
    ]
