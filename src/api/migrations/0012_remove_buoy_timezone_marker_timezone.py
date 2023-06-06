# Generated by Django 4.1 on 2023-03-03 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_alter_buoy_timezone_alter_marker_marker_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buoy',
            name='timezone',
        ),
        migrations.AddField(
            model_name='marker',
            name='timezone',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]