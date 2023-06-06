from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from ..models import SurfSpot
from ..serializers import (SurfSpotSerializer, AddSurfSpotSerializer)


class SurfSpotListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        surf_spots = request.user.surf_spots.all()
        serializer = SurfSpotSerializer(surf_spots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = AddSurfSpotSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        for spot_data in request.data:
            surf_spot = get_object_or_404(SurfSpot, id=spot_data['id'])
            spot_data['user'] = request.user.id
            serializer = AddSurfSpotSerializer(surf_spot, data=spot_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        surf_spot = get_object_or_404(SurfSpot, id=request.data['id'])
        surf_spot.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class SurfSpotRatingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, spot_id, *args, **kwargs):
        surf_spot = get_object_or_404(SurfSpot, id=spot_id)
        if surf_spot.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
