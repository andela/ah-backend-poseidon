from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Authors Heaven')

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

urlpatterns = [
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name='retrieve_user'),
    url(r'^users/?$', RegistrationAPIView.as_view(), name='authentication'),
    url(r'^users/login/?$', LoginAPIView.as_view(), name='login'),
    url(r'^swagger/', schema_view),
]
