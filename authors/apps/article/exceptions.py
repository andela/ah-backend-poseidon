"""
Exceptions file
define all custom exception classes
"""

from rest_framework.exceptions import APIException


class NotFoundException(APIException):
    """
    Provide default 404 error message
    """
    default_code = "not_found"
    default_detail = "The requested resource is not found."
    status_code = 404
