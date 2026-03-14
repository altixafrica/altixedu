# Migration for academics app - add AcademicYear and update models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_exam_examresult'),
        ('schools', '0003_school_subdomain_is_active'),
        ('teachers', '0001_initial'),
    ]

    operations = [
        # Create AcademicYear model
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(help_text='e.g., 2025/2026', max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=False, help_text='Only one academic year can be active per school')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='academic_years', to='schools.school')),
            ],
            options={
                'ordering': ['-year'],
            },
        ),
        
        # Add AcademicYear and class_teacher to Classroom
        migrations.AddField(
            model_name='classroom',
            name='academic_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='classrooms', to='academics.academicyear'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='class_teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='classes_taught', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='classroom',
            name='created_at',
            field=models.DateTimeField(default=timezone.now),
        ),
        
        # Update TeacherSubject with school_id and teacher reference
        migrations.AlterField(
            model_name='teachersubject',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects_taught', to='teachers.teacher'),
        ),
        migrations.AddField(
            model_name='teachersubject',
            name='school',
            field=models.ForeignKey(blank=True, help_text='Reference for multi-tenant data isolation', null=True, on_delete=django.db.models.deletion.CASCADE, to='schools.school'),
        ),
        
        # Update Classroom unique_together to include academic_year
        migrations.AlterUniqueTogether(
            name='classroom',
            unique_together={('school', 'name', 'academic_year')},
        ),
        
        # Add unique_together for AcademicYear
        migrations.AlterUniqueTogether(
            name='academicyear',
            unique_together={('school', 'year')},
        ),
    ]
