# Generated by Django 3.0.5 on 2020-05-23 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0010_auto_20200523_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='DoctorProfilePic/'),
        ),
    ]
