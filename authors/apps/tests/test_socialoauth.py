from urllib.parse import quote_plus

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import View
from oauth2_provider.models import (get_access_token_model,
                                    get_application_model)
from oauth2_provider.oauth2_backends import OAuthLibCore
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views import ProtectedResourceView
from oauth2_provider.views.mixins import OAuthLibMixin
from oauthlib.oauth2 import BackendApplicationServer
from rest_framework import status
from rest_framework.test import APITestCase

from ..authentication.models import User

Application = get_application_model()


class BaseTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.test_user = User.objects.create_user("test_user",
                                                  "test@example.com", "123456")
        self.dev_user = User.objects.create_user("dev_user", "dev@example.com",
                                                 "123456")

        self.application = Application(
            name="test_client_credentials_app",
            user=self.dev_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_CLIENT_CREDENTIALS,
        )
        self.application.save()

        oauth2_settings._SCOPES = ["read", "write"]
        oauth2_settings._DEFAULT_SCOPES = ["read", "write"]

    def tearDown(self):
        self.application.delete()
        self.test_user.delete()
        self.dev_user.delete()


class SocialOauthTest(BaseTest):
    def test_social_oauth(self):
        """
        Request an access token using Client Credential Flow
        """
        token_request_data = {
            "grant_type": "client_credentials",
        }
        client_id = self.application.client_id
        client_secret = self.application.client_secret
        backend = 'facebook'
        t1 = 'EAAKEAXI4rwQBAKZCZBCbLXDMnXlHxgW6lNxjJrRItYEqRbpwWkZCICDH68gXe'
        t2 = 'vlJSbYinoaidW0C3AJYyyypuE4Ee6wXyToKzZBGhJUA9EdAocX8c21Ii1ZAh0wbh'
        token = t1 + t2 + '2KSwxHgWj3X37UWP4iCDdLF7YF5XeF0lVAnKtCld2ZBbrbwZDZD'
        base_url = '/api/auth/convert-token?grant_type=convert_token&client'
        url = base_url + '_id=%s&client_secret=%s&backend=%s&token=%s' % (
            client_id, client_secret, backend, token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
