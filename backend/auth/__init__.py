"""
Authentication module for Vimarsh AI Agent

This module provides authentication and authorization functionality
including JWT validation and Microsoft Entra ID integration.
"""

from .entra_external_id_middleware import (
    EntraExternalIDMiddleware,
    VedUser,
    AuthenticationError,
    validate_jwt_token
)

__all__ = [
    'EntraExternalIDMiddleware',
    'VedUser', 
    'AuthenticationError',
    'validate_jwt_token'
]

__version__ = "1.0.0"
