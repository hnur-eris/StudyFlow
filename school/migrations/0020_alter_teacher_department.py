# Generated by Django 5.0.6 on 2024-05-21 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0019_student_studentdischargedetails_teacher_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='department',
            field=models.CharField(choices=[('Mathematics', 'Mathematics'), ('Literature', 'Literature'), ('Physic', 'Physic'), ('Chemistry', 'Chemistry'), ('Biology', 'Biology'), ('Software', 'Software')], default='Mathematic', max_length=50),
        ),
    ]
