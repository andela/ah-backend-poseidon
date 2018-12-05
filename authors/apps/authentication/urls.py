from django.conf.urls import url
from django.urls import path, include


from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView,
    ResetPasswordView, ResetPasswordView, ChangePasswordView, VerifyAccount
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name='retrieve_user'),
    path('users/', RegistrationAPIView.as_view(), name='authentication'),
    path('users/login/', LoginAPIView.as_view(), name='login'),
    path(
        'password-reset/', ResetPasswordView.as_view(), name='password-reset'),
    path(
        'password-reset/<str:token>/',
        ResetPasswordView.as_view(),
        name='password-reset'),
    path(
        'password/reset/done/',
        ChangePasswordView.as_view(),
        name='password-reset'),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^users/verify?$', VerifyAccount.as_view(), name='verifyemail')
]
