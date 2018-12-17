from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    status_code = 404
    default_detail = """Profile does not exist. Check provided username."""


class NotFollowSelf(APIException):
    status_code = 400
    default_detail = 'You can not follow yourself.'


class NotificationDoesNotExist(APIException):
    status_code = 404
    default_detail = """Notification does not exist"""


class NotificaionForbidden(APIException):
    status_code = 403
    default_detail = """Not permitted to view"""
