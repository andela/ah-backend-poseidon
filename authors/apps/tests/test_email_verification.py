import json
from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User

class TestEmailVerification(APITestCase):
    """Tests whether the confirmation email was sent successfully"""
    def test_confirmation_mail(self):
        data = {
            "user": {
                "username": "user",
                "email": "nuser@gmail.com",
                "password": 123456789,
            }
        }
        url = reverse('authentication')
        res = self.client.post(url, data, format='json')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            res.data['Message'],
            ' You have succesfully registerd to AH, please check your email for a confirmation link'
        )

    def test_account_verification(self):
        """
        Test for successful account verification
        """
        data = {
            "user": {
                "username": "user",
                "email": "user@gmail.com",
                "password": 123456789,
                }
        }
        url = reverse('authentication')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        token = response.data['token']
        verify_url = "/api/users/verify?token={}".format(token)
        res = self.client.get(verify_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(res.data['message'],
                      'Account succefully verified, you can now login')
