# Migration for accounts app - update User model with new fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('schools', '0003_school_subdomain_is_active'),
    ]

    operations = [
        # Add new fields to User
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_photo',
            field=models.ImageField(blank=True, help_text='User profile photo', null=True, upload_to='profile_photos/'),
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Update school FK with related_name
        migrations.AlterField(
            model_name='user',
            name='school',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='users', to='schools.school'),
        ),
        
        # Add unique constraint (school, email)
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('school', 'email')},
        ),
    ]
