from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .serializers import (UserSerializer,
                          FriendSerializer, FriendRequestSerializer, AddFriendRequestSerializer)
from .models import (FriendsList, FriendRequest)

# Create your views here.


class WaveTrackerRegistration(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        # Unique email
        if len(get_user_model().objects.filter(email=data['email'])) > 0:
            return Response({'email': 'An account with that email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        data['password'] = make_password(data['password'])
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WaveTrackerTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["email"] = user.email

        return token


class WaveTrackerTokenObtainPairView(TokenObtainPairView):
    serializer_class = WaveTrackerTokenObtainPairSerializer


class PublicProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = []

        users = get_user_model().objects.filter(~Q(username=request.user.username))
        search = request.GET.get('contains', None)
        limit = request.GET.get('limit', None)
        if search:
            users = users.filter(username__contains=search)
        if limit:
            if not limit.isdigit():
                return Response('Invalid value for limit', status=status.HTTP_406_NOT_ACCEPTABLE)

            users = users[:int(limit)]

        for user in users.all():
            username = user.get_username()
            data.append({
                'username': username,
                'url': f'/profile/{username}'
            })

        return Response(data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username, *args, **kwargs):
        user = request.user
        requested_user = get_object_or_404(get_user_model(), username=username)
        profile_data = {'total_surf_spots': len(requested_user.surf_spots.all()),
                        'total_surf_sessions': len(requested_user.surf_sessions.all())}


        return Response(profile_data, status=status.HTTP_200_OK)


class FriendsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friends_list = get_object_or_404(FriendsList, profile=user.profile)
        friends = friends_list.friends
        search = request.GET.get('username', None)
        if search:
            friends = friends.filter(username=search)

        serializer = FriendSerializer(friends.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user = request.user
        friends_list = get_object_or_404(FriendsList, profile=user.profile)

        friend = get_object_or_404(
            get_user_model(), username=request.data['user'])
        friends_list.add_friend(friend)

        return Response(status=status.HTTP_201_CREATED)


class FriendView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, friend_name, *args, **kwargs):
        user = request.user
        friends_list = get_object_or_404(FriendsList, profile=user.profile)
        friend = get_object_or_404(get_user_model(), username=friend_name)

        if friends_list.is_mutual_friend(friend):
            serializer = FriendSerializer(friend)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, friend_name, *args, **kwargs):
        user = request.user
        friends_list = get_object_or_404(FriendsList, profile=user.profile)
        friend = get_object_or_404(get_user_model(), username=friend_name)

        if friends_list.is_mutual_friend(friend):
            friends_list.unfriend(friend)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class FriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friend_requests = FriendRequest.objects.filter(
            Q(sender=user) | Q(receiver=user)).filter(is_active=True)
        profile_name = request.GET.get('user', None)
        if profile_name:
            profile = get_object_or_404(
                get_user_model(), username=profile_name)
            friend_requests = friend_requests.filter(
                Q(sender=profile) | Q(receiver=profile))

        serializer = FriendRequestSerializer(friend_requests.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data

        sender = request.user
        receiver = get_object_or_404(
            get_user_model(), username=data['receiver'])

        data['sender'] = sender.id
        data['receiver'] = receiver.id
        serializer = AddFriendRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class SentFriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        receiver_name = request.GET.get('receiver', None)

        requests = FriendRequest.objects.filter(
            sender=request.user).filter(is_active=True)
        if receiver_name:
            receiver = get_object_or_404(
                get_user_model(), username=receiver_name)
            requests = requests.filter(receiver=receiver.id)

        serializer = FriendRequestSerializer(requests.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceivedFriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sender_name = request.GET.get('sender', None)
        requests = FriendRequest.objects.filter(
            receiver=request.user).filter(is_active=True)
        if sender_name:
            sender = get_object_or_404(get_user_model(), username=sender_name)
            requests = requests.filter(sender=sender.id)

        serializer = FriendRequestSerializer(requests.all(), many=True)

        # Replace user id with username
        for friend_request in serializer.data:
            sender = get_object_or_404(
                get_user_model(), id=friend_request['sender'])
            friend_request['sender'] = sender.get_username()

        return Response(serializer.data, status=status.HTTP_200_OK)


class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        user = request.user
        friend_request = get_object_or_404(FriendRequest, id=id)

        if not (friend_request.sender == user or friend_request.receiver == user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_200_CREATED)

    def put(self, request, id, *args, **kwargs):
        user = request.user
        friend_request = get_object_or_404(FriendRequest, id=id)

        if not (friend_request.sender == user or friend_request.receiver == user):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        modification = request.data['modification']

        if modification == 'accept':
            friend_request.accept()
        elif modification == 'decline':
            friend_request.decline()
        elif modification == 'cancel':
            friend_request.cancel()
        else:
            return Response('Modification must be "accept" or "reject"', status=status.HTTP_400_BAD_REQUEST)

        return Response(f'Friend request modified: {modification}', status=status.HTTP_202_ACCEPTED)
