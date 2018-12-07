from .base import BaseTestCase
from rest_framework import status
from authors.apps.authentication.models import User
from . import (new_user, data2, invalid_email, invalid_password,
               short_password, dup_username, user_login)


class AccountTests(BaseTestCase):
    """handles user registration tests"""

    def test_new_user_registration(self):
        """check if new user can be registered"""
        response = self.register_user(new_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_user_login(self):
        """new user can be logged in\
        and token returned on successful login"""
        self.register_user(new_user)
        response = self.login_user(user_login)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_wrong_token_header_prefix(self):
        """invalid prefix header provided"""
        self.client.credentials(HTTP_AUTHORIZATION='hgfds ' + 'poiuytfd')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_for_invalid_token(self):
        """validates token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'yyuug')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_token_in_header(self):
        """no token in header"""
        self.add_credentials(response='')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_super_user(self):
        """checks for registration of a super user in the User model"""
        user = User.objects.create_superuser(
            username='ayebare',
            password='sampletestcase')
        self.assertIn(str(user), str(user.username))

    def test_create_non_user(self):
        """check for registration of a client user in the User model"""
        user = User.objects.create_user(
            email='m16ayebare@gmail.com',
            username='ayebare',
            password='sampletestcase')
        self.assertIn(str(user), str(user.email))

    def test_get_user_details(self):
        """get user details"""
        self.user_access()
        response = self.client.get('/api/user/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_details(self):
        """assert update route for user details is accessed"""
        self.user_access()
        response = self.client.put('/api/user/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_email_message(self):
        """test invalid email provided."""
        response = self.register_user(invalid_email)
        self.assertIn(response.data["errors"]["email"][0],
                      'Please enter a valid email in the format xxxx@xxx.xxx')

    def test_invalid_password(self):
        """asserts invalid password provided."""
        response = self.register_user(invalid_password)
        self.assertIn(response.data["errors"]["password"][0],
                      'Password should be alphanuemric (a-z,A_Z,0-9).')

    def test_short_password(self):
        """test short password provided."""
        response = self.register_user(short_password)
        self.assertIn(response.data["errors"]["password"][0],
                      'Password should not be less than 8 characters.')

    def test_duplicate_username(self):
        "user with same username provided exists"""
        self.register_user(new_user)
        response = self.register_user(dup_username)
        self.assertIn(response.data["errors"]["username"][0],
                      'user with this username already exists.')
