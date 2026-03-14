# Generated migration for personnel and assignment permissions

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('government', '0001_initial'),
    ]

    operations = [
        # Add new role choice
        migrations.AlterField(
            model_name='rolepermissiongroup',
            name='role',
            field=models.CharField(choices=[('super_admin', 'Super Admin'), ('ministry_admin', 'Ministry Admin'), ('school_admin', 'School Admin'), ('principal', 'Principal'), ('bursar', 'Bursar'), ('teacher', 'Teacher'), ('parent', 'Parent'), ('student', 'Student')], max_length=50),
        ),
        # Personnel management permissions
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_manage_teachers',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_manage_bursars',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_manage_staff',
            field=models.BooleanField(default=False),
        ),
        # Class & Assignment management permissions
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_manage_classrooms',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_assign_teachers_to_class',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_assign_students_to_class',
            field=models.BooleanField(default=False),
        ),
        # Parent & Student linking permissions
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_link_parent_student',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rolepermissiongroup',
            name='can_manage_parent_records',
            field=models.BooleanField(default=False),
        ),
    ]
