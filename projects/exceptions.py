# -*- coding: utf-8 -*-
"""
Useful exception classes that are used to return HTTP errors.
"""


class ApiException(Exception):
    """
    The base exception class for all APIExceptions.

    Parameters
    ----------
    code : str
        Error code.
    message : str
        Human readable string describing the exception.
    status_code : int
        HTTP status code.
    """

    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code


class BadRequest(ApiException):
    """
    Bad Request response status code indicates that the server cannot or will not
    process the request due to something that is perceived to be a client error.

    A common cause is that the client has sent invalid request values.
    """

    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=400)


class Forbidden(ApiException):
    """
    Forbidden client error status response code indicates that the server understands
    the request but refuses to authorize it.
    """

    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=403)


class NotFound(ApiException):
    """
    Not Found client error response code indicates that the server can't find the requested resource.

    A common cause is that a provided ID does not exist in the database.
    """

    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=404)


class InternalServerError(ApiException):
    """
    Internal Server Error server error response code indicates that the server
    encountered an unexpected condition that prevented it from fulfilling the request.

    This error response is a generic "catch-all" response.
    You should log error responses like the 500 status code with more details about
    the request to prevent the error from happening again in the future.
    """

    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=500)


class ServiceUnavailable(ApiException):
    """
    Service Unavailable server error response code indicates that the server is
    not ready to handle the request.

    A common cause is that the database is not available or overloaded.
    """

    def __init__(self, code: str, message: str):
        super().__init__(code, message, status_code=503)
