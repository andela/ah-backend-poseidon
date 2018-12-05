from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class AccountTests(APITestCase):
    """handles user registration tests"""
    def addcredentials(self,response):
        """this method adds authentication credentials in the request header"""
        self.client.credentials(
        HTTP_AUTHORIZATION='Token ' + response) 

    def test_new_user_registration(self):
        """check if new user can be registered and token returned"""
        url = reverse('authentication')
        data = {
            "user": {
                "username": "Jac",
                "email": "jak@jake.jake",
                "password": "jakejake"
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_user_login(self):
        """check if new user can be logged in and token returned on successful login"""
        url = reverse('authentication')
        data = {
            "user": {
                "username": "Jac",
                "email": "jak@jake.jake",
                "password": "jakejake"
            }
        }
        response = self.client.post(url, data, format='json')
        url = reverse('login')
        data = {"user": {"email": "jak@jake.jake", "password": "jakejake"}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get().username, 'Jac')
        self.assertIn("token", response.data)

    def test_wrong_token_header_prefix(self):
        """This test checks for response when wrong authoriation header prefix is entered"""
        self.client.credentials(HTTP_AUTHORIZATION='hgfds '+'poiuytfd')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_for_invalid_token(self):
        """This test checks for response when an invalid authorisation header is entered"""
        self.client.credentials(HTTP_AUTHORIZATION='Token '+'yyuug')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  

    def test_no_token_in_header(self):
        """This test checks for response when no authorization token is entered in the header"""
        self.addcredentials(response='')
        response = self.client.get("/api/user/", format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)      

    def test_create_super_user(self):
        """This test checks for registration of a super user in the User model"""
        user = User.objects.create_superuser(email='m16ayebare@gmail.com', username='ayebare', password='sampletestcase')
        self.assertIn(str(user),str(user.email))

    def test_create_non_user(self):
        """This test checks for registration of a client user in the User model"""
        user = User.objects.create_user(email='m16ayebare@gmail.com', username='ayebare', password='sampletestcase')
        self.assertIn(str(user),str(user.email))        

    def test_get_user_details(self):       
        """
        This test checks for access to the user get data endpoint upon
        entry of valid authentication token in the header
        """
        data = {"user":{'email': 'm16ayebare@gmail.com', 'username': 'ayebare', 'password':'sampletestcase'}}
        response = self.client.post('/api/users/', data, format='json')
        data = {"user":{'email': 'm16ayebare@gmail.com', 'password':'sampletestcase'}}
        response = self.client.post('/api/users/login', data, format='json')
        self.addcredentials(response.data['token'])
        response = self.client.get('/api/user/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  

    def test_update_user_details(self):
        """
        This test checks for access to the user update data endpoint upon
        entry of valid authentication token in the header
        """
        data = {"user":{'email': 'm16ayebare@gmail.com', 'username': 'ayebare', 'password':'sampletestcase'}}
        response = self.client.post('/api/users/', data, format='json')
        data= {"user":{'email': 'm16ayebare@gmail.com', 'password':'sampletestcase'}}
        response = self.client.post('/api/users/login', data, format='json')
        self.addcredentials(response.data['token'])
        response = self.client.put('/api/user/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
