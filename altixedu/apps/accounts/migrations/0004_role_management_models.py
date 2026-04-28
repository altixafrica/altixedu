from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0003_academicyear_and_updates'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('schools', '0006_school_ministry'),
        ('students', '0004_parent_student_user'),
        ('accounts', '0003_add_ministry_field'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('based_on', models.CharField(choices=[('superadmin', 'Super Admin'), ('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student'), ('parent', 'Parent'), ('bursar', 'Bursar')], help_text='Base role this custom role inherits from', max_length=20)),
                ('dashboard_template', models.CharField(blank=True, help_text='Custom dashboard layout for this role', max_length=50)),
                ('visible_modules', models.JSONField(blank=True, default=list, help_text='List of modules visible to this role')),
                ('can_manage_users', models.BooleanField(default=False)),
                ('can_manage_finances', models.BooleanField(default=False)),
                ('can_manage_academics', models.BooleanField(default=False)),
                ('can_view_reports', models.BooleanField(default=True)),
                ('can_export_data', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_roles', to=settings.AUTH_USER_MODEL)),
                ('permissions', models.ManyToManyField(blank=True, help_text='Select specific permissions for this role', to='auth.permission')),
                ('school', models.ForeignKey(blank=True, help_text='Leave blank for system-wide roles', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_roles', to='schools.school')),
            ],
            options={
                'ordering': ['school', 'name'],
                'unique_together': {('school', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ParentStudentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relationship', models.CharField(choices=[('mother', 'Mother'), ('father', 'Father'), ('guardian', 'Guardian'), ('grandparent', 'Grandparent'), ('sibling', 'Sibling'), ('other', 'Other')], max_length=50)),
                ('is_primary', models.BooleanField(default=False)),
                ('receives_progress_reports', models.BooleanField(default=True)),
                ('can_authorize_absence', models.BooleanField(default=False)),
                ('can_view_grades', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('linked_date', models.DateField(auto_now_add=True)),
                ('parent', models.ForeignKey(limit_choices_to={'role': 'parent'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_links', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_links', to='students.student')),
            ],
            options={
                'ordering': ['-is_primary', 'parent'],
                'unique_together': {('parent', 'student')},
            },
        ),
        migrations.CreateModel(
            name='RoleUserAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, help_text='Role assignment expiration date', null=True)),
                ('assigned_by', models.ForeignKey(limit_choices_to={'role': 'admin'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_roles', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.customrole')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='custom_role_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-assigned_at'],
                'unique_together': {('user', 'role')},
            },
        ),
        migrations.CreateModel(
            name='StudentClassroomAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('academic_year', models.CharField(help_text='Academic year (e.g., 2024-2025)', max_length=20)),
                ('roll_number', models.IntegerField(help_text="Student's roll number/seat number in the classroom")),
                ('is_active', models.BooleanField(default=True)),
                ('assigned_date', models.DateField(auto_now_add=True)),
                ('removed_date', models.DateField(blank=True, null=True)),
                ('removal_reason', models.CharField(blank=True, choices=[('promoted', 'Promoted'), ('demoted', 'Demoted'), ('transferred', 'Transferred'), ('graduated', 'Graduated'), ('dropped', 'Dropped Out'), ('other', 'Other')], max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='academics.classroom')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classroom_assignments', to='students.student')),
            ],
            options={
                'ordering': ['classroom', 'roll_number'],
                'unique_together': {('student', 'classroom', 'academic_year')},
            },
        ),
        migrations.AddIndex(
            model_name='parentstudentlink',
            index=models.Index(fields=['parent', 'is_active'], name='accounts_pa_parent__5772df_idx'),
        ),
        migrations.AddIndex(
            model_name='parentstudentlink',
            index=models.Index(fields=['student', 'is_primary'], name='accounts_pa_student_448ac9_idx'),
        ),
        migrations.AddIndex(
            model_name='studentclassroomassignment',
            index=models.Index(fields=['classroom', 'academic_year'], name='accounts_st_classro_b1de85_idx'),
        ),
        migrations.AddIndex(
            model_name='studentclassroomassignment',
            index=models.Index(fields=['student', 'is_active'], name='accounts_st_student_655f6e_idx'),
        ),
    ]
