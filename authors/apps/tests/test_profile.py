from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_validation import BaseTestCase
from . import new_user


class ProfileTestCase(BaseTestCase):
    "Handles users' profiles"

    def test_get_user_profile(self):
        self.register_user(new_user)
        url = reverse('get_profile', kwargs={'username': 'Jac'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_user_profile_who_does_not_exist(self):
        response = self.client.get(
            reverse('get_profile', kwargs={'username': 'john'}))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile(self):
        url = reverse('retrieve_user')
        res = self.register_user(new_user)
        self.add_credentials(res.data['token'])

        response = self.client.put(
            url,
            data={
                "user": {
                    "username": "jackson",
                    "email": "jack@dev.com",
                    "bio": "coder"
                }
            },
            format='json')
        self.assertEqual(response.data['bio'], 'coder')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
