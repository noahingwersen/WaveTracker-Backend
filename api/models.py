from django.db import models
from django.conf import settings
import datetime, pytz
from decimal import Decimal
from timezonefinder import TimezoneFinder
import requests
from statistics import mean

# Create your models here.


class Marker(models.Model):

    name = models.CharField(max_length=50, unique=True)
    latitude = models.DecimalField(max_digits=30, decimal_places=10)
    longitude = models.DecimalField(max_digits=30, decimal_places=10)
    timezone = models.CharField(max_length=50, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    marker_type = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        tzFinder = TimezoneFinder()
        timezone = pytz.timezone(tzFinder.timezone_at(lat=self.latitude, lng=self.longitude))
        self.timezone = timezone.zone
        self.marker_type = self.__class__.__name__
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Buoy(Marker):
    buoy_id = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f'{self.name}: {self.buoy_id}'


class SwellBuoy(Buoy):
    current_data = models.ForeignKey('SwellDataPoint', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    previous_data = models.ForeignKey('SwellDataPoint', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    def update_data(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        ninety_minutes = 5400
        if self.current_data is None or (now - self.current_data.date).seconds > ninety_minutes:
            lines = []
            for product in ('ss10', 'pm'):
                url = f"https://cdip.ucsd.edu/data_access/ndar?{self.buoy_id}+{product}+c{now.strftime('%Y%m%d%H%M')}"
                response = requests.get(url)
                response.raise_for_status()
                data = response.text.splitlines()

                if len(data) > 1:
                    line = data[-2]

                    if len(line.split()) < 8:
                        line = data[-3]

                    if '<pre>' in data[-2]:
                        line = line[5:len(line)]
                else:
                    line = None
                lines.append(line)

            swell_point = SwellDataPoint.create_from_cdip(*lines)
            swell_point.save()

            if self.previous_data:
                self.previous_data.delete()
            self.previous_data = self.current_data

            self.current_data = swell_point
            self.save()


class TideBuoy(Buoy):
    current_data = models.ForeignKey('TideDataPoint', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)
    previous_data = models.ForeignKey('TideDataPoint', related_name='+', on_delete=models.SET_NULL, blank=True, null=True)

    def update_data(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        six_minutes = 600
        if self.current_data is None or (now - self.current_data.date).seconds > six_minutes:
            baseUrl = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=Noah_Ingwersen&'
            url = f'{baseUrl}date=latest&datum=MLLW&station={self.buoy_id}&time_zone=GMT&units=english&interval=&format=json'

            response = requests.get(url)
            response.raise_for_status()

            json = response.json()
            currentPoint = json['predictions'][-1]
            date = pytz.utc.localize(datetime.datetime.strptime(
                currentPoint['t'], '%Y-%m-%d %H:%M'))
            height = Decimal(currentPoint['v'])

            tide_point = TideDataPoint(date=date, height=height)
            tide_point.save()

            if self.previous_data is not None:
                self.previous_data.delete()
            self.previous_data = self.current_data

            self.current_data = tide_point
            self.save()


class SurfSpot(Marker):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="surf_spots", on_delete=models.CASCADE, null=True)
    swell_buoy = models.ForeignKey(SwellBuoy, null=True, on_delete=models.SET_NULL)
    tide_buoy = models.ForeignKey(TideBuoy, null=True, on_delete=models.SET_NULL)

class SurfSession(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    surf_spot = models.ForeignKey(SurfSpot, related_name="surf_sessions", on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=30, decimal_places=4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='surf_sessions', null=True)

    def get_similarity(self, current_swell_data, current_tide_data) -> dict:
        swell_parameters = ('swell_height', 'swell_peak_period', 'swell_direction', 'swell_avg_period', 'sea_height',
        'sea_peak_period', 'sea_direction', 'sea_avg_period', 'wave_height', 'average_period')

        differences = dict()
        for parameter in swell_parameters: 
            average = mean([getattr(point, parameter) for point in self.swell_data.all()])
            differences[parameter] = abs(getattr(current_swell_data, parameter) - average)
        
        average_tide = mean([point.height for point in self.tide_data.all()])
        differences['tide_height'] = abs(current_tide_data.height - average_tide)
        
        return differences

    def __str__(self):
        return f'{self.start_date.strftime("%m/%d/%Y %H:%M")}-{self.end_date.strftime("%H:%M")} at {self.surf_spot.name}'


class SwellDataPoint(models.Model):
    surf_session = models.ForeignKey(SurfSession, related_name='swell_data', on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    swell_height = models.DecimalField(max_digits=30, decimal_places=4)
    swell_peak_period = models.DecimalField(max_digits=30, decimal_places=4)
    swell_direction = models.DecimalField(max_digits=30, decimal_places=4)
    swell_avg_period = models.DecimalField(max_digits=30, decimal_places=4)
    sea_height = models.DecimalField(max_digits=30, decimal_places=4)
    sea_peak_period = models.DecimalField(max_digits=30, decimal_places=4)
    sea_direction = models.DecimalField(max_digits=30, decimal_places=4)
    sea_avg_period = models.DecimalField(max_digits=30, decimal_places=4)

    # Can be blank
    wave_height = models.DecimalField(max_digits=30, decimal_places=4, blank=True)
    average_period = models.DecimalField(max_digits=30, decimal_places=4, blank=True)

    @classmethod
    def create_from_cdip(cls, seaSwellLine: str, overallLine: str = None):
        seaSwellData = seaSwellLine.split()
        date = datetime.datetime.strptime(seaSwellData[0], '%Y%m%d%H%M%S')
        point = cls(
            date               = pytz.utc.localize(date),
            swell_height        = Decimal(seaSwellData[1]),
            swell_peak_period    = Decimal(seaSwellData[2]),
            swell_direction     = Decimal(seaSwellData[3]),
            swell_avg_period     = Decimal(seaSwellData[4]),
            sea_height          = Decimal(seaSwellData[5]),
            sea_peak_period      = Decimal(seaSwellData[6]),
            sea_direction       = Decimal(seaSwellData[7]),
            sea_avg_period       = Decimal(seaSwellData[8])
        )

        # Overall Data
        if overallLine is not None:
            overallData = overallLine.split()
            point.wave_height         = Decimal(overallData[5])
            point.average_period      = Decimal(overallData[8])
        
        return point

class TideDataPoint(models.Model):
    surf_session = models.ForeignKey(SurfSession, related_name='tide_data', on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    height = models.DecimalField(max_digits=30, decimal_places=4)
    