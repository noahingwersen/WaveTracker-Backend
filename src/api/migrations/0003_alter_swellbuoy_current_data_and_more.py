# Generated by Django 4.1 on 2023-01-16 23:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_tidedatapoint_surf_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='swellbuoy',
            name='current_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.swelldatapoint'),
        ),
        migrations.AlterField(
            model_name='tidebuoy',
            name='current_data',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.tidedatapoint'),
        ),
    ]
