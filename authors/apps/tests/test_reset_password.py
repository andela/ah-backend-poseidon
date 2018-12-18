from authors.apps.authentication.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_validation import AccountTests

from . import (new_user, user_login)


class PassordResetTests(APITestCase):
    """handles user reseting passwordtests"""
    account_tests = AccountTests()

    def test_reset_user_password(self):
        """
        test validates whether email exits the it sends password
        reset lint to that email
        """
        self.client.post("/api/users/", new_user, format="json")
        self.client.post("/api/users/login/", user_login, format="json")
        response = self.client.post(
            "/api/password-reset/",
            data={"user": {
                "email": " jak@jake.jake"
            }},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data['Message'],
                      "A link has been sent to your email")

    def test_confirm_reset_user_password_status_code(self):
        """
        test ckecks whether token is in the link the user has clicked
        on his mail
        """
        response = self.client.get(
            "/api/password-reset/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9."
            "eyJpZCI6NCwiZW1haWwiOiJnYWJyaWVsQGdtYWlsLmNvbSIsImV4cCI6MTU0NDQ1NjIzNH0."
            "O4x6zL17kRthBPFP1MrYES3TjY34j4rlS7u-Gm4pwSc"
            "/",
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert "token" in response.data

    def test_confirm_reset_without_token(self):
        """
        Tests checks for return of error when user doesnt have token
        """
        response = self.client.put("/api/password/reset/done/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            response.data['detail'],
            "ErrorDetail(string='Authentication credentials were not provided.',"
            "code='not_authenticated')")

    def test_confirm_reset(self):
        """"This method tests successful reseting of a user password"""

        self.password_update = {"user": {"password": "Newpaswd1"}}
        res = self.client.post("/api/users/", new_user, format="json")
        token = res.data['token']
        response = self.client.get("/api/password-reset/{}/".format(token))
        token = response.data['token']
        self.add_credentials(response.data['token'])
        response = self.client.put(
            "/api/password/reset/done/",
            data=self.password_update,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response.data['Message'],
                      "Your password has been updated succesfully")

    def add_credentials(self, response):
        """adds authentication credentials in the request header"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response)
