from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_alter_fee_options_fee_currency_code_fee_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fee',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='studentfee',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='paymentreceipt',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Amount paid', max_digits=12),
        ),
        migrations.AlterField(
            model_name='paymentreceipt',
            name='amount_in_usd',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Converted amount in USD for reporting (calculated via exchange rate)',
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='paymentreceipt',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('cash', 'Cash'),
                    ('check', 'Check'),
                    ('transfer', 'Bank Transfer'),
                    ('card', 'Card'),
                    ('mobile_money', 'Mobile Money'),
                    ('m_pesa', 'M-Pesa'),
                    ('airtel_money', 'Airtel Money'),
                    ('mtn_money', 'MTN Mobile Money'),
                    ('flutterwave', 'Flutterwave'),
                    ('other', 'Other'),
                ],
                default='cash',
                max_length=20,
            ),
        ),
    ]
