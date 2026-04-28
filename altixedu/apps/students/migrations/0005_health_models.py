from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encryption


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_parent_student_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentEmergencyContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', encryption.EncryptedCharField(max_length=200)),
                ('relationship', models.CharField(help_text='Relationship to student (Parent, Guardian, Relative, etc.)', max_length=50)),
                ('phone_number', encryption.EncryptedCharField(max_length=20)),
                ('email', encryption.EncryptedCharField(blank=True, max_length=255)),
                ('address', encryption.EncryptedField(blank=True)),
                ('is_primary', models.BooleanField(default=False)),
                ('priority_order', models.IntegerField(default=0)),
                ('preferred_contact_method', models.CharField(choices=[('phone', 'Phone'), ('email', 'Email'), ('sms', 'SMS')], default='phone', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contacts', to='students.student')),
            ],
            options={
                'ordering': ['priority_order', '-is_primary'],
            },
        ),
        migrations.CreateModel(
            name='StudentHealthRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medical_conditions', models.TextField(blank=True, help_text='Comma-separated list of medical conditions (e.g., Asthma, Diabetes)')),
                ('allergies', encryption.EncryptedField(blank=True, help_text='Allergies and sensitivities (food, medications, environmental)')),
                ('medications', encryption.EncryptedField(blank=True, help_text='Current medications and dosages')),
                ('insurance_provider', encryption.EncryptedCharField(blank=True, help_text='Health insurance provider name', max_length=255)),
                ('insurance_policy_number', encryption.EncryptedCharField(blank=True, help_text='Insurance policy/member ID', max_length=100)),
                ('immunization_status', models.CharField(blank=True, choices=[('up_to_date', 'Up to Date'), ('needs_update', 'Needs Update'), ('unknown', 'Unknown')], max_length=50)),
                ('blood_type', models.CharField(blank=True, choices=[('O+', 'O+'), ('O-', 'O-'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-')], help_text='Student blood type', max_length=5)),
                ('height_cm', models.FloatField(blank=True, help_text='Height in centimeters', null=True)),
                ('weight_kg', models.FloatField(blank=True, help_text='Weight in kilograms', null=True)),
                ('wears_glasses', models.BooleanField(default=False)),
                ('hearing_impairment', models.BooleanField(default=False)),
                ('special_needs', models.TextField(blank=True, help_text='Any special needs or accommodations required')),
                ('last_medical_checkup', models.DateField(blank=True, help_text='Date of last medical checkup', null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='health_record', to='students.student')),
            ],
        ),
        migrations.CreateModel(
            name='HealthMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_type', models.CharField(choices=[('height', 'Height'), ('weight', 'Weight'), ('blood_pressure', 'Blood Pressure'), ('bmi', 'BMI'), ('fitness_score', 'Fitness Score')], max_length=50)),
                ('value', models.CharField(max_length=100)),
                ('unit', models.CharField(help_text='Unit of measurement (cm, kg, mmHg, etc.)', max_length=20)),
                ('recorded_date', models.DateField()),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recorded_by', models.ForeignKey(help_text='Staff member who recorded the metric', limit_choices_to={'role__in': ['teacher', 'admin']}, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='health_metrics', to='students.student')),
            ],
            options={
                'ordering': ['-recorded_date'],
            },
        ),
    ]
