"""
Authentication and Authorization System
JWT tokens, email verification, password reset
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import User, VerificationToken
from database import get_db

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # CHANGE THIS
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
VERIFICATION_TOKEN_EXPIRE_HOURS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_verification_token(db: Session, user_id: int, token_type: str) -> str:
    """Create email verification or password reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS)
    
    verification_token = VerificationToken(
        user_id=user_id,
        token=token,
        token_type=token_type,
        expires_at=expires_at
    )
    db.add(verification_token)
    db.commit()
    return token

def verify_token(token: str, db: Session, token_type: str) -> Optional[User]:
    """Verify a verification token and return user"""
    token_obj = db.query(VerificationToken).filter(
        VerificationToken.token == token,
        VerificationToken.token_type == token_type,
        VerificationToken.used == False,
        VerificationToken.expires_at > datetime.utcnow()
    ).first()
    
    if not token_obj:
        return None
    
    # Mark token as used
    token_obj.used = True
    db.commit()
    
    # Get and return user
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended"
        )
    
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin status"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

