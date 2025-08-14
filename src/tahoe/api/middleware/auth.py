"""
Authentication middleware for Tahoe API
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Get service token from environment
SERVICE_TOKEN = os.getenv("TAHOE_SERVICE_TOKEN", "development_token_change_in_production")
TOKEN_HASH = hashlib.sha256(SERVICE_TOKEN.encode()).hexdigest()


async def verify_service_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verify the service token for API authentication
    
    Args:
        credentials: Bearer token from request header
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    # Hash the provided token
    provided_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Use constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(provided_hash, TOKEN_HASH):
        logger.warning("Invalid service token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True


def get_optional_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Optional token verification for endpoints that can work with or without auth
    
    Returns:
        Token if provided, None otherwise
    """
    try:
        if credentials:
            return verify_service_token(credentials)
    except:
        pass
    return None