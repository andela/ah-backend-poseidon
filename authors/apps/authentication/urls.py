from django.urls import path
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Authors Heaven')

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    ResetPasswordView, ResetPasswordView, ChangePasswordView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='retrieve_user'),
    path('users/', RegistrationAPIView.as_view(), name='authentication'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path('swagger/', schema_view),
    path('password-reset/', ResetPasswordView.as_view(), name='password-reset'),
    path('password-reset/<str:token>/',
         ResetPasswordView.as_view(), name='password-reset'),
    path('password/reset/done/', ChangePasswordView.as_view(), name='password-reset'),
]
