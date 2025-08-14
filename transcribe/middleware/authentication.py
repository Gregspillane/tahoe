"""
JWT authentication middleware for the Transcription Service.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.settings import Settings

security = HTTPBearer()
settings = Settings()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Validate JWT token and return user information.
    For MVP, we'll use a simple token validation.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        
        # For MVP, simple token comparison
        # In production, implement proper JWT validation
        if token != settings.service_auth_token:
            raise credentials_exception
        
        # Return mock user for now
        return {"sub": "service", "type": "service_token"}
        
    except JWTError:
        raise credentials_exception