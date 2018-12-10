from rest_framework import status, serializers
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response

from .exceptions import ProfileDoesNotExist, NotFollowSelf
from .models import Profile
from .serializers import ProfileSerializer
from .renderers import ProfileJSONRenderer


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
    serializer_class = ProfileSerializer

    def post(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        if follower.pk is followee.pk:
            raise NotFollowSelf

        follower.follow(followee)
        serializer = self.serializer_class(
            followee, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, username=None):
        follower = self.request.user.profile

        try:
            followee = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise ProfileDoesNotExist

        follower.unfollow(followee)

        serializer = self.serializer_class(
            followee, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
