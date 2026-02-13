"""Middleware package for application-wide request processing."""

from app.middleware.role_verification import RoleVerificationMiddleware

__all__ = ["RoleVerificationMiddleware"]
