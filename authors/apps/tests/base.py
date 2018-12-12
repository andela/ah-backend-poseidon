from django.urls import reverse
from rest_framework.test import APITestCase
from . import (new_user, user_login, post_article, post_article_2, data2,
               ARTICLE_URL)


class BaseTestCase(APITestCase):
    "Has test helper methods."

    def add_credentials(self, response):
        """adds authentication credentials in the request header"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response)

    def register_user(self, user_data):
        """register new user"""
        url = reverse('authentication')
        return self.client.post(url, user_data, format='json')

    def verify_user(self, user_data):
        response = self.register_user(user_data)
        token = response.data['token']
        verify_url = "/api/users/verify?token={}".format(token)
        res = self.client.get(verify_url)
        return res

    def verify_user_invalid_link(self, user_data):
        response = self.register_user(user_data)
        token = response.data['token']
        verify_url = "api/users/rewdhdfgj?token={}".format(token)
        res = self.client.get(verify_url)
        return res

    def login_user(self, user_data):
        """login existing user"""
        url = reverse('login')
        return self.client.post(url, user_data, format='json')

    def user_access(self):
        """signup and login user"""
        self.verify_user(new_user)
        response = self.login_user(user_login)
        self.add_credentials(response.data['token'])

    def posting_article(self, post_data):
        url = reverse("articles")
        return self.client.post(url, data=post_data, format='json')

    def slugger(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get('/api/articles', format='json')
        data = response.json().get("articles")[0]
        return data["slug"]

    def deleter(self, slug):
        return self.client.delete(
            reverse("get_update_destroy_article", kwargs=dict(slug=slug)),
            format='json')

    def authorize_user(self):
        res = self.register_user(new_user)
        self.add_credentials(res.data["token"])

    def authorize_user2(self):
        res = self.register_user(data2)
        self.add_credentials(res.data["token"])

    def rate_article(self, rating):
        self.authorize_user2()
        response = self.client.get(ARTICLE_URL, format='json')
        data = response.json().get("articles")[0]
        slug = data["slug"]

        return self.client.post(
            reverse("rating", kwargs=dict(slug=slug)),
            data={"article": {
                "score": rating
            }},
            format="json")

    def post_articles_for_search(self):
        self.authorize_user()
        self.posting_article(post_article)
        self.posting_article(post_article_2)
