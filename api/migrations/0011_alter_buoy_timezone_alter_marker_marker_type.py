# Generated by Django 4.1 on 2023-02-03 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_surfsession_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buoy',
            name='timezone',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='marker',
            name='marker_type',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
