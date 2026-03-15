# Generated migration for subdomain and is_active fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0002_ministry'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='subdomain',
            field=models.CharField(blank=True, default='', help_text='Subdomain for accessing school (e.g., \'muse\' for muse.altixedu.com)', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='school',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Superadmin can suspend schools'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['subdomain'], name='schools_sch_subdom_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['is_active'], name='schools_sch_is_act_idx'),
        ),
    ]
