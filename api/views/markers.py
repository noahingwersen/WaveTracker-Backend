from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from ..models import (SwellBuoy, TideBuoy)
from ..serializers import (
    BuoySerializer, SurfSpotSerializer)


class MarkerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializers = [
            BuoySerializer,
            BuoySerializer,
            SurfSpotSerializer
        ]
        markers = [
            SwellBuoy.objects.all(),
            TideBuoy.objects.all(),
            request.user.surf_spots.all()
        ]

        data = []
        for serializer_class, marker_type in zip(serializers, markers):
            for marker in marker_type:
                serializer = serializer_class(marker)
                data.append(serializer.data)

        return Response(data, status=status.HTTP_200_OK)
