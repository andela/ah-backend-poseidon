from django.conf.urls import url
from django.urls import path
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Authors Heaven')

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,VerifyAccount
)

urlpatterns = [
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name='retrieve_user'),
    url(r'^users/?$', RegistrationAPIView.as_view(), name='authentication'),
    url(r'^users/login/?$', LoginAPIView.as_view(), name='login'),
    url(r'^users/verify?$', VerifyAccount.as_view(), name='verifyemail'),
    url(r'^swagger/', schema_view)
]