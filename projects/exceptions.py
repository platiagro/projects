# -*- coding: utf-8 -*-


class BadRequest(Exception):
    def __init__(self, message: str):
        self.message = message
        self.code = 400


class ForbiddenRequest(Exception):
    def __init__(self, message: str):
        self.message = message
        self.code = 403


class NotFound(Exception):
    def __init__(self, message: str):
        self.message = message
        self.code = 404


class InternalServerError(Exception):
    def __init__(self, message: str):
        self.message = message
        self.code = 500
