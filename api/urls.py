from django.urls import path
from .views.markers import MarkerListView
from .views.buoys import (BuoyListView, SwellBuoyListView,
                          TideBuoyListView, SwellBuoyDataView, TideBuoyDataView)
from .views.surfspots import (SurfSpotListView)
from .views.surfsessions import (
    SurfSessionListView, SimilarSurfSessionView, SurfSessionDataView, UserStatView)

urlpatterns = [
    path('markers/', MarkerListView.as_view()),
    path('buoys/', BuoyListView.as_view()),
    path('buoys/swell/', SwellBuoyListView.as_view()),
    path('buoys/tide/', TideBuoyListView.as_view()),
    path('buoys/swell/<int:id>/data/', SwellBuoyDataView.as_view()),
    path('buoys/tide/<int:id>/data/', TideBuoyDataView.as_view()),
    path('spots/', SurfSpotListView.as_view()),
    path('spots/<int:spot_id>/sessions/', SurfSessionListView.as_view()),
    path('spots/<int:spot_id>/sessions/closest/',
         SimilarSurfSessionView.as_view()),
    path('sessions/<int:session_id>/data/', SurfSessionDataView.as_view()),
    path('users/<str:username>/stats/', UserStatView.as_view())
]
