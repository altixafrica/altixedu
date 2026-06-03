from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_remove_student_parents_delete_studentparent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='admission_number',
            field=models.CharField(help_text='Unique per school', max_length=50),
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.UniqueConstraint(
                fields=('school', 'admission_number'),
                name='unique_student_admission_number_per_school',
            ),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['school', 'admission_number'], name='students_st_school_d4740a_idx'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['school', 'status'], name='students_st_school_790111_idx'),
        ),
    ]
