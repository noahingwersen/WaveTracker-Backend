from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (WaveTrackerRegistration, WaveTrackerTokenObtainPairView, FriendsListView, PublicProfileListView, FriendView, ProfileView,
                    SentFriendRequestListView, ReceivedFriendRequestListView, FriendRequestListView, FriendRequestView)

urlpatterns = [
    path('register/', WaveTrackerRegistration.as_view()),
    path('token/', WaveTrackerTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('usernames/', PublicProfileListView.as_view()),
    path('friends/', FriendsListView.as_view()),
    path('friends/<str:friend_name>/', FriendView.as_view()),
    path('profile/<str:username>/', ProfileView.as_view()),
    path('friendrequests/', FriendRequestListView.as_view()),
    path('friendrequests/<int:id>/', FriendRequestView.as_view()),
    path('friendrequests/sent/', SentFriendRequestListView.as_view()),
    path('friendrequests/received/',
         ReceivedFriendRequestListView.as_view()),
]
