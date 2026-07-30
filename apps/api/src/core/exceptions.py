"""
Axorks OS — Custom Exceptions & Global Handlers

Structured error responses that never leak internal details.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse


# ── Custom Exception Classes ─────────────────────────────────


class AppException(Exception):
    """Base exception for Axorks OS application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str = "Resource", identifier: str | None = None):
        msg = f"{resource} not found"
        if identifier:
            msg = f"{resource} '{identifier}' not found"
        super().__init__(message=msg, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppException):
    """Resource conflict — e.g., duplicate email (409)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class ForbiddenError(AppException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class UnauthorizedError(AppException):
    """Authentication required or failed (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)


class ValidationError(AppException):
    """Input validation failed (422)."""

    def __init__(self, message: str = "Validation failed", errors: list | None = None):
        self.errors = errors or []
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class BadRequestError(AppException):
    """Bad request (400)."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)


class RateLimitError(AppException):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ── Global Exception Handlers ───────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "meta": None,
                "errors": [{"message": exc.detail}],
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "data": None,
                "meta": None,
                "errors": [{"message": exc.detail}],
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log the real error server-side but never expose to client
        import logging

        logging.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "data": None,
                "meta": None,
                "errors": [{"message": "An internal error occurred"}],
            },
        )
