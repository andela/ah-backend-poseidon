"""
Test articles app
"""
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.utils import json

from authors.apps.article.models import Article
from authors.apps.authentication.models import User


class TestArticle(TestCase):
    """
    test class to contain functions to handle test for the article
    """
    post_article = {
        "article": {
            "title": "Who is he",
            "description": "He has a bald head",
            "body": "He has ruled Uganda for over 30 years"
        }
    }
    update_article = {
        "article": {
            "title": "Who is he and why is he here",
            "description": "He has a bald head",
            "body": "He has ruled Uganda for over 30 years"
        }
    }
    article_missing_data = {
        "article": {
            "description": "He has a bald head",
            "body": "He has ruled Uganda for over 30 years"
        }
    }

    def posting_article(self):
        return self.client.post(
            "/api/articles/", data=json.dumps(
                self.post_article), content_type='application/json')

    def slugger(self):
        self.posting_article()

        response = self.client.get(
            "/api/articles/", content_type='application/json')
        data = response.json().get("articles")[0]

        return data["slug"]

    def deleter(self, slug):
        return self.client.delete(
            "/api/articles/{0}/".format(slug), content_type='application/json')

    def setUp(self):
        """
        setup tests for article app
        :return:
        """
        # delete any users in the test database
        User.objects.all().delete()
        # delete any articles in the test database
        Article.objects.all().delete()

        self.login_data = {"user": {"email": "arnold.katumba@gmail.com", "password": "qawsedrf", }
                           }
        self.registration_data = {"user": {"username": "Arnold", "email": "arnold.katumba@gmail.com",
                                           "password": "qawsedrf", }}
        self.client = APIClient()
        # signup new user
        self.response = self.client.post("/api/users/", self.registration_data, format="json")
        # login user
        self.response = self.client.post("/api/users/login/", self.login_data, format="json")
        self.assertEqual(status.HTTP_200_OK, self.response.status_code)
        self.assertIn('token', self.response.data)
        token = self.response.data.get("token", None)
        self.client.credentials(HTTP_AUTHORIZATION="Token {0}".format(token))

    def test_post_new_article(self):
        response = self.posting_article()
        self.assertEqual(201, response.status_code)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_post_article_with_missing_data(self):
        response = self.client.post(
            "/api/articles/", data=json.dumps(
                self.article_missing_data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.json())

    def test_no_articles(self):
        response = self.client.get(
            "/api/articles/", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), list)

    def test_get_all_articles(self):
        count = 0
        while count < 3:
            self.posting_article()
            count += 1

        response = self.client.get(
            "/api/articles/", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json().get("articles")), 3)

    def test_get_specific_article(self):

        slug = self.slugger()

        response = self.client.get(
            "/api/articles/{0}/".format(slug), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_get_article(self):

        self.posting_article()

        response = self.client.get(
            "/api/articles/", content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("articles", response.json())
        self.assertIsInstance(response.json().get("articles"), list)

    def test_update_article(self):

        slug = self.slugger()

        response = self.client.put(
            "/api/articles/{0}/".format(slug), data=json.dumps(
                self.update_article), content_type='application/json')
        self.assertEqual(response.status_code, 202)
        self.assertIn('articles', response.json())
        self.assertIsInstance(response.json().get("articles"), dict)

    def test_delete_specific_article(self):
        slug = self.slugger()
        response = self.deleter(slug)
        self.assertEqual(response.status_code, 204)
        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data.get("detail"), str)

    def test_delete_not_found_article(self):
        response = self.client.delete(
            "/api/articles/54/", content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data.get("detail"), str)




