from .base import BaseTestCase
from rest_framework import status
from django.urls import reverse

from authors.apps.profiles.models import Notification
from . import (new_user, new_user_2, user2_login, user_login, new_username,
               post_article, data2)


class NotificationTests(BaseTestCase):
    """handles notification tests"""

    def setUp(self):
        self.user_access()

    def test_notification_creation(self):
        self.create_notification(new_username)
        notification = Notification.objects.get(user__username='Jac')
        no_of_notifications = Notification.objects.count()
        self.assertGreaterEqual(no_of_notifications, 1)

    def test_notification_endpoint(self):
        url = reverse('notify')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications', response.json())

    def test_retrieve_single_notification(self):
        url = reverse(
            'single_notify',
            kwargs={'pk': self.create_notification(new_username)})
        response = self.client.get(url, format='json')
        self.assertFalse(response.data['status'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_non_existing_notification(self):
        url = reverse('single_notify', kwargs={'pk': '8'})
        response = self.client.get(url, format='json')
        self.assertIn('notifications', response.json())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_notification_update(self):
        url = reverse(
            'single_notify',
            kwargs={'pk': self.create_notification(new_username)})
        response = self.client.put(url, format='json')
        self.assertTrue(response.data['status'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_delete(self):
        url = reverse(
            'single_notify',
            kwargs={'pk': self.create_notification(new_username)})
        response = self.client.delete(url)
        self.assertIn('Notification has been deleted', response.data['detail'])

    def test_notification_forbidden(self):
        self.user2_access()
        url = reverse(
            'single_notify',
            kwargs={'pk': self.create_notification(new_username)})
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_existant_notification_update(self):
        url = reverse('single_notify', kwargs={'pk': '8'})
        response = self.client.put(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_notification_after_article(self):
        res = self.register_user(data2)
        token = res.data['token']
        self.client.put(
            reverse('user_follow', kwargs={'username': 'Jacko'}))
        verify_url = "/api/users/verify?token={}".format(token)
        self.client.get(verify_url)
        self.login_user(data2)
        self.add_credentials(token)
        self.posting_article(post_article)
        res2 = self.login_user(new_user)
        self.add_credentials(res2.data['token'])
        url = reverse('notify')
        response = self.client.get(url, format='json')
        self.assertFalse(response.data[0]['status'])
        self.assertIn('Jacko', response.data[0]['body'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
