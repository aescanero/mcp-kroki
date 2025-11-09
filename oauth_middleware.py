#!/usr/bin/env python3
"""OAuth 2.1 Authentication Middleware for MCP Kroki Server"""

import os
import logging
from typing import Optional
from fastapi import HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7662 import IntrospectionToken
from jose import JWTError, jwt
import requests

logger = logging.getLogger(__name__)

# OAuth 2.1 Configuration
OAUTH_ENABLED = os.getenv("OAUTH_ENABLED", "false").lower() == "true"
OAUTH_ISSUER = os.getenv("OAUTH_ISSUER", "")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")
OAUTH_AUDIENCE = os.getenv("OAUTH_AUDIENCE", "")
OAUTH_INTROSPECTION_URL = os.getenv("OAUTH_INTROSPECTION_URL", "")
OAUTH_JWKS_URL = os.getenv("OAUTH_JWKS_URL", "")
OAUTH_TOKEN_VALIDATION = os.getenv("OAUTH_TOKEN_VALIDATION", "introspection")  # introspection or jwks

security = HTTPBearer(auto_error=False)


class OAuthValidator:
    """OAuth 2.1 Token Validator"""

    def __init__(self):
        self.enabled = OAUTH_ENABLED
        self.issuer = OAUTH_ISSUER
        self.client_id = OAUTH_CLIENT_ID
        self.client_secret = OAUTH_CLIENT_SECRET
        self.audience = OAUTH_AUDIENCE
        self.introspection_url = OAUTH_INTROSPECTION_URL
        self.jwks_url = OAUTH_JWKS_URL
        self.validation_method = OAUTH_TOKEN_VALIDATION
        self.jwks = None

        if self.enabled:
            logger.info(f"OAuth 2.1 authentication enabled")
            logger.info(f"Issuer: {self.issuer}")
            logger.info(f"Validation method: {self.validation_method}")

            if self.validation_method == "jwks" and self.jwks_url:
                self._load_jwks()
        else:
            logger.info("OAuth 2.1 authentication disabled")

    def _load_jwks(self):
        """Load JWKS (JSON Web Key Set) from the issuer"""
        try:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            self.jwks = response.json()
            logger.info("JWKS loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load JWKS: {e}")
            self.jwks = None

    def validate_token_introspection(self, token: str) -> dict:
        """Validate token using OAuth 2.1 token introspection endpoint"""
        try:
            response = requests.post(
                self.introspection_url,
                auth=(self.client_id, self.client_secret),
                data={"token": token, "token_type_hint": "access_token"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            response.raise_for_status()
            token_info = response.json()

            if not token_info.get("active", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is not active or has been revoked",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Validate audience if configured
            if self.audience:
                aud = token_info.get("aud", [])
                if isinstance(aud, str):
                    aud = [aud]
                if self.audience not in aud:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid audience. Expected: {self.audience}",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            return token_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Token introspection failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service unavailable",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def validate_token_jwks(self, token: str) -> dict:
        """Validate token using JWKS (JSON Web Key Set)"""
        if not self.jwks:
            self._load_jwks()

        if not self.jwks:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="JWKS not available",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Decode and validate JWT
            payload = jwt.decode(
                token,
                self.jwks,
                algorithms=["RS256", "RS384", "RS512"],
                audience=self.audience if self.audience else None,
                issuer=self.issuer if self.issuer else None,
                options={
                    "verify_signature": True,
                    "verify_aud": bool(self.audience),
                    "verify_iss": bool(self.issuer),
                    "verify_exp": True,
                }
            )
            return payload

        except JWTError as e:
            logger.error(f"JWT validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def validate_token(self, token: str) -> dict:
        """Validate token using configured validation method"""
        if self.validation_method == "jwks":
            return self.validate_token_jwks(token)
        else:
            return self.validate_token_introspection(token)


# Global validator instance
oauth_validator = OAuthValidator()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Dependency to get the current authenticated user
    Returns None if OAuth is disabled
    Returns user info if OAuth is enabled and token is valid
    Raises HTTPException if OAuth is enabled and token is invalid
    """
    # If OAuth is disabled, allow all requests
    if not oauth_validator.enabled:
        return None

    # If OAuth is enabled, require valid token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token_info = oauth_validator.validate_token(credentials.credentials)
        return token_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def optional_authentication(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[dict]:
    """
    Optional authentication dependency
    Returns user info if valid token is provided, None otherwise
    Does not raise exceptions for missing or invalid tokens
    """
    if not oauth_validator.enabled:
        return None

    if credentials is None:
        return None

    try:
        token_info = oauth_validator.validate_token(credentials.credentials)
        return token_info
    except Exception as e:
        logger.warning(f"Optional authentication failed: {e}")
        return None
