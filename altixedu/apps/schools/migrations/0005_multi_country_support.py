# Generated migration for multi-country support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0004_alter_school_options_and_more'),
    ]

    operations = [
        # Add new fields to Ministry for multi-country support
        migrations.AddField(
            model_name='ministry',
            name='state_or_province',
            field=models.CharField(
                max_length=100,
                default='Unknown',
                help_text='State/Province/Region name'
            ),
        ),
        migrations.AddField(
            model_name='ministry',
            name='currency_code',
            field=models.CharField(
                max_length=3,
                default='NGN',
                help_text='ISO 4217 currency code'
            ),
        ),
        migrations.AddField(
            model_name='ministry',
            name='currency_symbol',
            field=models.CharField(
                max_length=5,
                default='₦',
                help_text='Currency symbol'
            ),
        ),
        
        # Update state field to remove unique constraint
        migrations.AlterField(
            model_name='ministry',
            name='state',
            field=models.CharField(
                max_length=100,
                unique=False,
                help_text='Legacy field - use state_or_province instead'
            ),
        ),
        
        # Update unique constraint on Ministry
        migrations.AlterUniqueTogether(
            name='ministry',
            unique_together={('country', 'state_or_province')},
        ),
    ]
