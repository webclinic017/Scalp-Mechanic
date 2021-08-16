## Imports
from __future__ import annotations


## Variables
__all__ = [

]


## Classes
class SessionException(Exception):
    """Base exception class for Session"""
    pass


class WebsocketException(SessionException):
    """Base exception class for Websocket"""
    pass


class LoginException(SessionException):
    """Base exception class for login failures"""
    pass


class LoginInvalidException(LoginException):
    """Login exception for invalid requests"""

    def __init__(self, message: str) -> LoginInvalidException:
        super().__init__(message)


class LoginCaptchaException(LoginException):
    """Login exception for rate limiting"""

    def __init__(self, ticket: str, time: int, captcha: bool) -> LoginInvalidException:
        message = ("Unable to login due to rate limiting. Ticket: "
                  f"{ticket}, {time} seconds. Captcha required: {captcha}")
        super().__init__(message)
