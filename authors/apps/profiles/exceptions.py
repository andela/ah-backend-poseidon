from rest_framework.exceptions import APIException
from rest_framework import status


class ProfileDoesNotExist(APIException):
    status_code = 404
    default_detail = """Profile does not exist. Check provided username."""


class NotFollowSelf(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'You can not follow yourself.'


class NotificationDoesNotExist(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = """Notification does not exist"""


class NotificaionForbidden(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = """Not permitted to view"""
