"""Service token authentication for agent-engine"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
from .models.api import AuthContext


# Security scheme for FastAPI
security = HTTPBearer()


async def verify_service_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> AuthContext:
    """
    Verify service token from Authorization header
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        AuthContext with token information
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    # Get expected token from environment
    expected_token = os.getenv("SERVICE_TOKEN")
    
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service token not configured"
        )
    
    # Verify token matches
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return auth context
    return AuthContext(
        token=credentials.credentials,
        service_name="agent-engine",
        permissions=["read", "write", "admin"]  # Full permissions for service token
    )


def get_optional_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))
) -> Optional[AuthContext]:
    """
    Optional authentication - returns None if no token provided
    
    Args:
        credentials: Optional bearer token
        
    Returns:
        AuthContext if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    expected_token = os.getenv("SERVICE_TOKEN")
    if not expected_token or credentials.credentials != expected_token:
        return None
    
    return AuthContext(
        token=credentials.credentials,
        service_name="agent-engine",
        permissions=["read", "write", "admin"]
    )