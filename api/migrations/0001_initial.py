# Generated by Django 4.1 on 2023-01-16 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Marker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('latitude', models.DecimalField(decimal_places=4, max_digits=30)),
                ('longitude', models.DecimalField(decimal_places=4, max_digits=30)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('marker_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SurfSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('rating', models.DecimalField(decimal_places=4, max_digits=30)),
            ],
        ),
        migrations.CreateModel(
            name='Buoy',
            fields=[
                ('marker_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.marker')),
                ('timezone', models.CharField(max_length=50)),
                ('buoy_id', models.PositiveIntegerField(unique=True)),
            ],
            bases=('api.marker',),
        ),
        migrations.CreateModel(
            name='SurfSpot',
            fields=[
                ('marker_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.marker')),
            ],
            bases=('api.marker',),
        ),
        migrations.CreateModel(
            name='TideDataPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('height', models.DecimalField(decimal_places=4, max_digits=30)),
                ('surf_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.surfsession')),
            ],
        ),
        migrations.CreateModel(
            name='SwellDataPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('swell_height', models.DecimalField(decimal_places=4, max_digits=30)),
                ('swell_peak_period', models.DecimalField(decimal_places=4, max_digits=30)),
                ('swell_direction', models.DecimalField(decimal_places=4, max_digits=30)),
                ('swell_avg_period', models.DecimalField(decimal_places=4, max_digits=30)),
                ('sea_height', models.DecimalField(decimal_places=4, max_digits=30)),
                ('sea_peak_period', models.DecimalField(decimal_places=4, max_digits=30)),
                ('sea_direction', models.DecimalField(decimal_places=4, max_digits=30)),
                ('sea_avg_period', models.DecimalField(decimal_places=4, max_digits=30)),
                ('wave_height', models.DecimalField(blank=True, decimal_places=4, max_digits=30)),
                ('average_period', models.DecimalField(blank=True, decimal_places=4, max_digits=30)),
                ('surf_session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.surfsession')),
            ],
        ),
        migrations.AddField(
            model_name='surfsession',
            name='surf_spot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.surfspot'),
        ),
        migrations.CreateModel(
            name='TideBuoy',
            fields=[
                ('buoy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.buoy')),
                ('current_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.tidedatapoint')),
            ],
            bases=('api.buoy',),
        ),
        migrations.CreateModel(
            name='SwellBuoy',
            fields=[
                ('buoy_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.buoy')),
                ('current_data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.swelldatapoint')),
            ],
            bases=('api.buoy',),
        ),
        migrations.AddField(
            model_name='surfspot',
            name='swell_buoy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.swellbuoy'),
        ),
        migrations.AddField(
            model_name='surfspot',
            name='tide_buoy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tidebuoy'),
        ),
    ]
