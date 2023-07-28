from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from ..models import (Buoy, SwellBuoy, TideBuoy)
from ..serializers import (BuoySerializer, SwellBuoySerializer, TideBuoySerializer, SwellDataPointSerializer, TideDataPointSerializer)

import pytz


class BuoyListView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        buoys = Buoy.objects.all()
        serializer = BuoySerializer(buoys, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SwellBuoyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        swell_buoys = SwellBuoy.objects.all()
        serializer = BuoySerializer(swell_buoys, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SwellBuoySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TideBuoyListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, *args, **kwargs):
        swell_buoys = TideBuoy.objects.all()
        serializer = BuoySerializer(swell_buoys, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = TideBuoySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SwellBuoyDataView(APIView):

    def get(self, request, id, *args, **kwargs):
        buoy = get_object_or_404(SwellBuoy, pk=id)
        buoy.update_data()
        display_timezone = request.GET.get('timezone', None)

        serializer = SwellDataPointSerializer(buoy.current_data)
        data = serializer.data

        if display_timezone and display_timezone == 'local':
            timezone = pytz.timezone(buoy.timezone)
            data['date'] = buoy.current_data.date.astimezone(timezone)

        return Response(data, status=status.HTTP_200_OK)


class TideBuoyDataView(APIView):

    def get(self, request, id, *args, **kwargs):
        buoy = get_object_or_404(TideBuoy, pk=id)
        buoy.update_data()
        display_timezone = request.GET.get('timezone', None)

        serializer = TideDataPointSerializer(buoy.current_data)
        data = serializer.data

        if display_timezone and display_timezone == 'local':
            timezone = pytz.timezone(buoy.timezone)
            data['date'] = buoy.current_data.date.astimezone(timezone)

        return Response(data, status=status.HTTP_200_OK)
