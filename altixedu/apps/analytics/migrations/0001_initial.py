from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalyticsDashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_students', models.IntegerField(default=0)),
                ('students_at_risk_count', models.IntegerField(default=0)),
                ('average_attendance_rate', models.FloatField(default=0.0)),
                ('average_performance_rate', models.FloatField(default=0.0)),
                ('total_fees_due', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_fees_collected', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('collection_rate_percentage', models.FloatField(default=0.0)),
                ('total_teachers', models.IntegerField(default=0)),
                ('active_classrooms', models.IntegerField(default=0)),
                ('enrollment_growth_rate', models.FloatField(default=0.0, help_text='Month-over-month growth %')),
                ('attendance_trend', models.CharField(choices=[('improving', 'Improving'), ('stable', 'Stable'), ('declining', 'Declining')], default='stable', max_length=10)),
                ('calculated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_dashboard', to='schools.school')),
            ],
            options={
                'verbose_name_plural': 'Analytics Dashboards',
            },
        ),
        migrations.CreateModel(
            name='SchoolPerformanceMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('total_present', models.IntegerField(default=0)),
                ('total_absent', models.IntegerField(default=0)),
                ('attendance_rate', models.FloatField(default=0.0)),
                ('average_score', models.FloatField(default=0.0)),
                ('students_above_threshold', models.IntegerField(default=0)),
                ('students_below_threshold', models.IntegerField(default=0)),
                ('fees_collected_today', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('outstanding_fees', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='performance_metrics', to='schools.school')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('school', 'date')},
            },
        ),
    ]
