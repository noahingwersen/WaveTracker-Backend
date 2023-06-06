from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from ..models import (SurfSpot, SurfSession, SwellBuoy,
                      TideBuoy, SwellDataPoint, TideDataPoint)
from ..serializers import (SurfSessionSerializer,
                           SurfSessionWithDataSerializer, SwellDataPointSerializer, TideDataPointSerializer)

import requests
import math
import datetime
import pytz

DATE_FORMATS = {
    'ISO-YMD': '%Y-%M-%DT%H:%M:%SZ',
    'standard': '%m/%d/%Y %H:%M:%S'
}


class SurfSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, spot_id, *args, **kwargs):
        surf_spot = get_object_or_404(SurfSpot, id=spot_id)
        if not (surf_spot.user == request.user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        sessions = SurfSession.objects.filter(surf_spot=surf_spot)
        serializer = SurfSessionSerializer(sessions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, spot_id, *args, **kwargs):
        data = request.data

        data['surf_spot'] = spot_id
        data['user'] = request.user.id

        serializer = SurfSessionSerializer(data=data)
        if serializer.is_valid():
            session = serializer.save()
            self._get_data(session)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _get_swell_data(self, surf_session: SurfSession, buoy: SwellBuoy, start: datetime, end: datetime):
        products = ["ss10", "pm"]
        productData = []
        for product in products:
            dateString = start.strftime(
                "%Y%m%d%H%M") + "-" + end.strftime("%Y%m%d%H%M")
            url = f"https://cdip.ucsd.edu/data_access/ndar?{buoy.buoy_id}+{product}+{dateString}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.text.splitlines()
            productData.append(data)

        for i in range(len(productData[0]) - 1):
            lines = []
            for data in productData:
                line = data[i]
                if i == 0:
                    index = len(line) - 5
                    line = line[-index:]
                lines.append(line)

            swell_point = SwellDataPoint.create_from_cdip(*lines)
            swell_point.surf_session = surf_session
            swell_point.save()

    def _get_tide_data(self, surf_session: SurfSession, buoy: TideBuoy, start: datetime, end: datetime):
        baseUrl = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?product=predictions&application=Noah_Ingwersen&'
        startString = start.strftime('%Y%m%d %H:%M')
        endString = end.strftime('%Y%m%d %H:%M')

        url = f'{baseUrl}begin_date={startString}&end_date={endString}&datum=MLLW&station={buoy.buoy_id}&time_zone=GMT&units=english&interval=&format=json'
        response = requests.get(url)
        response.raise_for_status()

        for prediction in response.json()['predictions']:
            date = pytz.utc.localize(datetime.datetime.strptime(
                prediction['t'], '%Y-%m-%d %H:%M'))
            tide_point = TideDataPoint(
                date=date, height=prediction['v'], surf_session=surf_session)
            tide_point.save()

    def _get_data(self, session: SurfSession):
        self._get_swell_data(session, session.surf_spot.swell_buoy,
                             session.start_date, session.end_date)
        self._get_tide_data(session, session.surf_spot.tide_buoy,
                            session.start_date, session.end_date)


class SurfSessionDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id, *args, **kwargs):
        session = get_object_or_404(SurfSession, id=session_id)
        if not session.user == request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = SurfSessionWithDataSerializer(session)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SimilarSurfSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, spot_id, *args, **kwargs):
        surf_spot = get_object_or_404(SurfSpot, id=spot_id)
        date_format = request.GET.get('date_format', None)
        sessions = SurfSession.objects.filter(
            surf_spot=surf_spot, user=request.user)

        closest_score = math.inf
        closest_session = None
        surf_spot.swell_buoy.update_data()
        surf_spot.tide_buoy.update_data()
        swell_data = surf_spot.swell_buoy.current_data
        tide_data = surf_spot.tide_buoy.current_data
        for session in sessions.all():
            value_differences = session.get_similarity(swell_data, tide_data)

            total = sum(value_differences.values())
            if total < closest_score:
                closest_score = total
                closest_session = session

        session_serializer = SurfSessionWithDataSerializer(closest_session)
        swell_serializer = SwellDataPointSerializer(swell_data)
        tide_serializer = TideDataPointSerializer(tide_data)

        session_data = session_serializer.data
        print(date_format is not None and date_format in DATE_FORMATS)
        if date_format is not None and date_format in DATE_FORMATS:
            session_data['start_date'] = closest_session.start_date.strftime(
                DATE_FORMATS[date_format])
            session_data['end_date'] = closest_session.end_date.strftime(
                DATE_FORMATS[date_format])

        data = {
            'similar_session': session_data,
            'timezone': surf_spot.timezone,
            'current_swell_data': swell_serializer.data,
            'current_tide_data': tide_serializer.data
        }

        return Response(data, status=status.HTTP_200_OK)


class UserStatView(APIView):
    def get(self, request, username, *args, **kwargs):
        user = get_object_or_404(get_user_model(), username=username)

        data = {
            'session_stats': self._get_session_stats(user),
            'spot_stats': self._get_spot_stats(user)
        }

        return Response(data, status=status.HTTP_200_OK)

    def _get_session_stats(self, user) -> dict:
        sessions = user.surf_sessions.all()
        now = datetime.datetime.now()
        this_year_sessions = sessions.filter(start_date__year=now.year)
        this_month_sessions = this_year_sessions.filter(
            start_date__month=now.month)

        session_data = {
            'total': len(sessions),
            'year': len(this_year_sessions),
            'month': len(this_month_sessions)
        }

        return session_data

    def _get_spot_stats(self, user) -> dict:
        surf_spots = user.surf_spots.all()
        now = datetime.datetime.now()

        this_year_spots = surf_spots.filter(
            surf_sessions__start_date__year=now.year)

        spot_data = {
            'total': len(surf_spots),
            'year': len(this_year_spots)
        }

        return spot_data
