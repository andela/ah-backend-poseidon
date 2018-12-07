import json

from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User

from . import invalid_email, new_user
from .test_validation import AccountTests


class TestEmailVerification(AccountTests):
    def test_mail_sent_successfully(self):
        """Tests whether the confirmation email was sent successfully"""
        res = self.register_user(new_user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            res.data['Message'],
            ' You have succesfully registerd to AH, please check your email for a confirmation link'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_account_verification(self):
        """
        Test for successful account verification
        """
        res = self.verify_user(new_user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(res.data['message'],
                      'Account succefully verified, you can now login')

    def test_invalid_verification_link(self):
        res = self.verify_user_invalid_link(new_user)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_failed_verification(self):
        """ Test verification fails when user registration does not go through. """
        response = self.register_user(invalid_email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)
