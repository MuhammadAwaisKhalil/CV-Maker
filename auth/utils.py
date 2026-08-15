import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings
from db.utils import get_user_by_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Exact relative or absolute path matching the mounted login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(plain_password:str):
    return pwd_context.hash(plain_password)

def verify_password(plain_password:str, hash_password:str):
    return pwd_context.verify(plain_password, hash_password)

def create_access_token(user_id:int)->str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRY_DAYS)

    payload = {"sub":str(user_id),"exp":expire}

    return jwt.encode(payload, settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """Decodes the JWT Bearer token and returns the authenticated user's ID."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id:str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)
    except Exception as e:
        raise credentials_exception


    user = get_user_by_id(user_id)
    if not user:
        raise credentials_exception

    return user_id


