from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    status_code = 400
    default_detail = """Profile does not exist. Cross-check the provided username."""


class NotFollowSelf(APIException):
    status_code = 400
    default_detail = 'You can not follow yourself.'
