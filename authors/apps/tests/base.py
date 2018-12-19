from django.urls import reverse
from rest_framework.test import APITestCase
from . import (new_user, user_login, post_article, post_article_2, data2,
               ARTICLE_URL, user2_login, new_user_2)
from authors.apps.authentication.models import User
from authors.apps.article.models import Article
from authors.apps.profiles.models import Notification


class BaseTestCase(APITestCase):
    """Has test helper methods."""

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

    def user2_access(self):
        """signup and login user2"""
        self.verify_user(new_user_2)
        response = self.login_user(user2_login)
        self.add_credentials(response.data['token'])

    def posting_article(self, post_data):
        url = reverse("articles")
        return self.client.post(url, data=post_data, format='json')

    def slugger(self):
        self.authorize_user_reg()
        self.posting_article(post_article)
        response = self.client.get('/api/articles', format='json')
        data = response.json().get("articles")
        return data["results"][0]["slug"]

    def slugger2(self):
        self.authorize_user()
        self.posting_article(post_article)
        response = self.client.get('/api/articles', format='json')
        data = response.json().get("articles")
        return data["results"][0]["slug"]

    def deleter(self, slug):
        """
        delete an article
        """
        return self.client.delete(
            reverse("get_update_destroy_article", kwargs=dict(slug=slug)),
            format='json')

    def authorize_user(self):
        """
        register new user and escape email verification process
        """
        res = self.register_user(new_user)
        self.add_credentials(res.data["token"])

    def authorize_user_reg(self):
        res = self.login_user(new_user)
        self.add_credentials(res.data["token"])

    def authorize_user2(self):
        """
        authorize the second user's access

        """
        res = self.register_user(data2)
        self.add_credentials(res.data["token"])

    def rate_article(self, rating):
        """
        rate an article
        """
        self.authorize_user2()
        response = self.client.get(ARTICLE_URL, format='json')
        data = response.json().get("articles")
        slug = data["results"][0]["slug"]

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

    def favouring(self, slug):
        """
        choose an article as favourite article
        """
        return self.client.put(
            reverse("favourite", kwargs=dict(slug=slug)), format="json")

    def undo_favouring(self, slug):
        """
        delete an article from your favourites article
        """
        return self.client.delete(
            reverse("undo_favourite", kwargs=dict(slug=slug)), format="json")

    def create_notification(self, username):
        user = User.objects.get(username=username)
        title = 'create article'
        body = 'article has been created'
        notify = Notification(user=user, type=title, body=body)
        notify.save()
        return notify.id

    def regiter_user_and_post_article(self):
        self.user_access()
        self.posting_article(post_article)
        return True

    def create_test_article_with_user(self):
        author = User(
            username=new_user_2['user']['username'],
            email=new_user_2['user']['email'],
            password=new_user['user']['password'])
        author.save()

        article = Article(
            author=author, body='lorem ipsum', title='lorem ipsum')
        article.save()
        return article

    def remove_all_articles(self):
        Article.objects.all().delete()

    def data_for_bookmarks(self):
        self.post_articles_for_search()
        self.authorize_user2()
        article_data = self.client.get(ARTICLE_URL, format='json')
        data = article_data.json().get("articles")
        slug = data["results"][0]["slug"]
        return slug

    def url_for_bookmarks(self):
        slug = self.data_for_bookmarks()
        url = reverse('bookmark_article', kwargs={'slug': slug})
        return url

    def url_for_invalid_slug(self):
        slug = self.data_for_bookmarks()
        slug = slug + 'hello'
        url = reverse('bookmark_article', kwargs={'slug': slug})
        return url

    def create_superuser(self, username, password):
        user = User.objects.create_superuser(
            username=username, password=password)

    def login_superuser(self):
        username = new_user['user']['username']
        password = new_user['user']['password']
        self.create_superuser(username, password)
        response = self.login_user(user_login)
        self.add_credentials(response.data['token'])

    def return_new_article_id(self):
        article = self.posting_article(post_article)
        return article.data['id']

    def report_article(self, report_data):
        self.user2_access()
        id = self.return_new_article_id()
        url = reverse('report_article', kwargs={'pk': id})
        response = self.client.post(url, data=report_data, format='json')
        return response
