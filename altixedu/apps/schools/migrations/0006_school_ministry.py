from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0005_multi_country_support'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='ministry',
            field=models.ForeignKey(
                blank=True,
                help_text='Ministry that provisioned or governs this school',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='schools',
                to='schools.ministry',
            ),
        ),
    ]
