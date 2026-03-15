# Generated migration for payment approval threshold currency support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('government', '0002_add_personnel_permissions'),
    ]

    operations = [
        # Add currency fields to PaymentApprovalThreshold
        migrations.AddField(
            model_name='paymentapprovalthreshold',
            name='country',
            field=models.CharField(
                max_length=100,
                default='Nigeria',
                help_text='Country'
            ),
        ),
        migrations.AddField(
            model_name='paymentapprovalthreshold',
            name='currency_code',
            field=models.CharField(
                max_length=3,
                default='NGN',
                help_text='ISO 4217 currency code (NGN, KES, GHS, ZAR, etc.)'
            ),
        ),
    ]
