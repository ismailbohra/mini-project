"""Custom exceptions for the application."""

from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    """Exception raised when user is not found."""

    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserAlreadyExistsException(HTTPException):
    """Exception raised when user already exists."""

    def __init__(self, detail: str = "User already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidCredentialsException(HTTPException):
    """Exception raised when credentials are invalid."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InactiveUserException(HTTPException):
    """Exception raised when user is inactive."""

    def __init__(self, detail: str = "Inactive user"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthorizedException(HTTPException):
    """Exception raised when user is not authorized."""

    def __init__(self, detail: str = "Not authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
