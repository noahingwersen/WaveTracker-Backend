from django.contrib import admin
from profiles.models import Profile, FriendsList, FriendRequest

# Register your models here.
admin.site.register([Profile, FriendsList, FriendRequest])
