from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from .exceptions import (NotFollowSelf, ProfileDoesNotExist,
                         NotificationDoesNotExist)
from .models import Notification, Profile
from .utilities import return_notification
from .renderers import NotificationJSONRenderer, ProfileJSONRenderer
from .serializers import NotificationSerializer, ProfileSerializer


def get_follows(**kwargs):
    "Handles getting and serializing a user's followers or followings"
    data = []
    message = 'Currently you have no follows.'
    for follower in kwargs['follows']:
        serializer = kwargs['serializer'](
            follower, context={
                'request': kwargs['request']
            })
        data.append(serializer.data)

    if len(data) is 0:
        data.append(message)

    return data


class ProfileRetrieveAPIView(generics.RetrieveAPIView):
    """
      Implements user's profile endpoint.
    """

    permission_classes = (permissions.AllowAny, )
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)
        profile = {'profile': serializer.data}

        return Response(profile, status=status.HTTP_200_OK)


class FollowAuthorAPIView(generics.GenericAPIView):
    """
    Implements user following and unfollowing endpoints.
    """

    permission_classes = (permissions.IsAuthenticated, )
    renderer_classes = (ProfileJSONRenderer, )

    def put(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        if follower.pk is followee.pk:
            raise NotFollowSelf

        follower.follow(followee)
        serializer = ProfileSerializer(
            followee, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        follower.unfollow(followee)

        serializer = ProfileSerializer(
            followee, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class ListAuthorsAPIView(generics.ListAPIView):
    """
    Implements listing of all users' profiles
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    renderer_classes = (ProfileJSONRenderer, )
    permission_classes = (permissions.IsAuthenticated, )


class UserNotificationsView(generics.GenericAPIView):
    """
      Return user's notification
    """
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = NotificationSerializer
    renderer_classes = (NotificationJSONRenderer, )

    def get(self, request):
        query = Notification.objects.filter(user_id=request.user.pk)
        serializer = NotificationSerializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationRetrieveAPIView(generics.GenericAPIView):
    """
      Return user's notification
    """
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = NotificationSerializer
    renderer_classes = (NotificationJSONRenderer, )

    def get(self, request, pk):
        query = return_notification(request, pk)
        serializer = NotificationSerializer(query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        query = return_notification(request, pk)
        query.status = True
        query.save()
        serializer = NotificationSerializer(query)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        query = return_notification(request, pk)
        query.delete()
        return Response({'detail': 'Notification has been deleted'})
class FollowersAPIView(generics.ListAPIView):
    """
    Implements listing all user's followers
    """
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user = request.user.profile
        followers = user.followers()
        data = get_follows(
            follows=followers,
            request=request,
            serializer=self.serializer_class)

        return Response({'followers': data})


class FollowsAPIView(generics.ListAPIView):
    """
    Implements listing all users that the user is following
    """
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user = request.user.profile
        follows = user.follows.all()

        data = get_follows(
            follows=follows, request=request, serializer=self.serializer_class)

        return Response({'following': data})
