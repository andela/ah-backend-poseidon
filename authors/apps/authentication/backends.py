import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        This method checks each client's request for authentication
        """
        # returns none if no authentication is required for a given request
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1 or len(auth_header) > 2:
            return None

        header_prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if header_prefix.lower() != auth_header_prefix:
            return None

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        """
        This method checks the token sent in a request for valid user credentials.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid Authentication'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(email=payload['email'])
        except User.DoesNotExist:
            msg = 'No user with the provided credentials'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
