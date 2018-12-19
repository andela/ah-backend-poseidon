from .base import BaseTestCase
from rest_framework import status
from django.urls import reverse

from authors.apps.profiles.models import Notification
from . import (user_login, post_article, report_data, invalid_report_data_int,
               invalid_report_data_blank)
from ..article.utils import invalid_string


class NotificationTests(BaseTestCase):
    """
    Tests for the notification function
    """
    def test_return_reports(self):
        self.login_superuser()
        url = reverse('all_reports')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_normaluser_forbidden(self):
        self.user2_access()
        url = reverse('all_reports')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_artilce(self):
        response = self.report_article(report_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_invalid_data(self):
        response = self.report_article(invalid_report_data_blank)
        self.assertIn(invalid_string, response.data['details'])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_single_report(self):
        report = self.report_article(report_data)
        report_id = report.data['id']
        self.login_superuser()
        url = reverse('single_report', kwargs={'pk': report_id})
        response = self.client.get(url)
        self.assertTrue(response.data['viewed'], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_report_doesnt_exist(self):
        self.login_superuser()
        url = reverse('single_report', kwargs={'pk': 5})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_single_report(self):
        report = self.report_article(report_data)
        report_id = report.data['id']
        self.login_superuser()
        url = reverse('single_report', kwargs={'pk': report_id})
        response = self.client.put(url)
        self.assertTrue(response.data['violation'], True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_single_report(self):
        report = self.report_article(report_data)
        report_id = report.data['id']
        self.login_superuser()
        url = reverse('single_report', kwargs={'pk': report_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
