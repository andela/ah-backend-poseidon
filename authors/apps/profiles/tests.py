from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Profile


class ProfileTestCase(APITestCase):

    data = {
           "user": {
            "username": "jac",
            "email": "jak@jake.jake",
            "password": "jakejake"
            }
        }

    def test_get_user_profile(self):
        url = reverse('authentication')
        self.client.post(url, self.data, format='json')
        url = reverse('get_profile', kwargs={'username': 'jac'})
        response = self.client.get(url, self.data, format='json')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_get_user_profile_who_does_not_exist(self):
        response = self.client.get(reverse('get_profile',
                                   kwargs={'username': 'john'}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_profilex(self):
        res = self.client.post(reverse('authentication'), self.data,
                               format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + res.data['token'])
        url = reverse('retrieve_user')
        
        response = self.client.put(url, data={"user": {"username": "jackson",
                                   "email": "jack@dev.com", "bio": "coder"}},
                                   format='json')
        self.assertEqual(response.data['bio'], 'coder')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
