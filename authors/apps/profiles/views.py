from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .exceptions import ProfileDoesNotExist
from .models import Profile
from .serializers import ProfileSerializer


class ProfileRetrieveAPIView(RetrieveAPIView):
    """
      Returns user's profile.
    """
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer

    def retrieve(self, request, username, *args, **kwargs):
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except Profile.DoesNotExist as e:
            raise ProfileDoesNotExist

        serializer = self.serializer_class(profile)
        profile = {'profile': serializer.data}

        return Response(profile, status=status.HTTP_200_OK)
