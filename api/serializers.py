from rest_framework import serializers
from .models import (Marker, Buoy, SwellBuoy, TideBuoy,
                     SurfSpot, SwellDataPoint, TideDataPoint, SurfSession)


class MarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marker
        fields = ['id', 'name', 'latitude',
                  'longitude', 'added_at', 'marker_type']


class BuoySerializer(serializers.ModelSerializer):
    class Meta:
        model = Buoy
        fields = ['id', 'name', 'latitude', 'longitude',
                  'buoy_id', 'timezone', 'added_at', 'marker_type']


class SwellBuoySerializer(serializers.ModelSerializer):
    class Meta:
        model = SwellBuoy
        fields = ['name', 'latitude', 'longitude', 'buoy_id', 'timezone']


class TideBuoySerializer(serializers.ModelSerializer):
    class Meta:
        model = TideBuoy
        fields = ['name', 'latitude', 'longitude', 'buoy_id', 'timezone']


class SurfSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurfSession
        fields = '__all__'


class AddSurfSpotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurfSpot
        fields = ['user', 'name', 'latitude', 'longitude',
                  'swell_buoy', 'tide_buoy']


class SurfSpotSerializer(serializers.ModelSerializer):
    surf_sessions = SurfSessionSerializer(many=True, required=False)

    class Meta:
        model = SurfSpot
        fields = '__all__'
        depth = 2


class SwellDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SwellDataPoint
        exclude = ['surf_session']


class TideDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = TideDataPoint
        exclude = ['surf_session']


class SurfSessionWithDataSerializer(serializers.ModelSerializer):
    swell_data = SwellDataPointSerializer(many=True)
    tide_data = TideDataPointSerializer(many=True)

    class Meta:
        model = SurfSession
        fields = '__all__'
        depth = 2
