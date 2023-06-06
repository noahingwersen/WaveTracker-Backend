from django.db import models
from django.conf import settings
from django.shortcuts import get_object_or_404

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f'{self.user.username}\'s Profile'


class FriendsList(models.Model):
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name='friends_list')
    friends = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='friends_lists')

    def add_friend(self, account):
        if not account in self.friends.all():
            self.friends.add(account)

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)

    def unfriend(self, account):
        self.remove_friend(account)
        FriendsList.objects.get(
            profile=account.profile).remove_friend(self.profile.user)

    def is_mutual_friend(self, friend):
        return friend in self.friends.all()

    def __str__(self):
        return f'{self.profile.user.username}\'s Friends List'


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    is_active = models.BooleanField(blank=True, null=False, default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def accept(self):
        receiver_friend_list = get_object_or_404(
            FriendsList, profile=self.receiver.profile)
        sender_friend_list = get_object_or_404(
            FriendsList, profile=self.sender.profile)

        receiver_friend_list.add_friend(self.sender)
        sender_friend_list.add_friend(self.receiver)

        self.is_active = False
        self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()

    def __str__(self):
        return f'{self.sender.username} to {self.receiver.username}'
