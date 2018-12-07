from django.urls import reverse
from rest_framework.test import APITestCase
from . import (new_user, user_login)


class BaseTestCase(APITestCase):
    "Has test helper methods."

    def add_credentials(self, response):
        """adds authentication credentials in the request header"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response)

    def register_user(self, user_data):
        """register new user"""
        url = reverse('authentication')
        return self.client.post(url, user_data, format='json')

    def login_user(self, user_data):
        """login existing user"""
        url = reverse('login')
        return self.client.post(url, user_data, format='json')

    def user_access(self):
        """signup and login user"""
        self.register_user(new_user)
        response = self.login_user(user_login)
        self.add_credentials(response.data['token'])
