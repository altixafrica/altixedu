# Generated migration for ministry field in User

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0003_school_subdomain_is_active'),
        ('accounts', '0002_user_updates'),
    ]

    operations = [
        # Add ministry_admin role to ROLE_CHOICES
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('superadmin', 'Super Admin'), ('admin', 'School Admin'), ('ministry_admin', 'Ministry Admin'), ('teacher', 'Teacher'), ('student', 'Student'), ('parent', 'Parent'), ('bursar', 'Bursar')], max_length=20),
        ),
        # Add ministry FK field
        migrations.AddField(
            model_name='user',
            name='ministry',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='admin_users',
                to='schools.ministry',
                help_text='Required for ministry_admin role (restricts to their state)'
            ),
        ),
    ]
