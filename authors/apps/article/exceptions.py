"""
Exceptions file
define all custom exception classes
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class NotFoundException(APIException):
    """
    Provide default 404 error message
    """
    default_code = "not_found"
    default_detail = "The requested resource is not found."
    status_code = status.HTTP_404_NOT_FOUND


class ReportDoesNotExist(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = """Report does not exist"""
