"""
Authentication Service

Handles user registration, login, password hashing, and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt
from pydantic import EmailStr

from src.models.user import User, UserRole
from src.core.config import settings


class AuthService:
    """
    User authentication service.
    
    Handles:
    - User registration (driver or admin)
    - Password hashing and verification
    - JWT token creation and validation
    - User login
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(user_id: int, role: UserRole, expires_delta: Optional[timedelta] = None) -> Dict:
        """
        Create JWT access token.
        
        Returns:
        {
            "access_token": "...",
            "token_type": "bearer",
            "expires_in": 604800
        }
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        
        to_encode = {
            "sub": str(user_id),
            "role": role.value,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict]:
        """
        Verify JWT token and extract user info.
        
        Returns:
        {
            "user_id": 1,
            "role": "driver"
        }
        or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id: int = int(payload.get("sub"))
            role: str = payload.get("role")
            
            if user_id is None or role is None:
                return None
            
            return {"user_id": user_id, "role": role}
        except JWTError:
            return None
    
    @staticmethod
    def register_user(db: Session, email: EmailStr, password: str, 
                     full_name: str, phone: Optional[str] = None,
                     role: UserRole = UserRole.DRIVER) -> Dict:
        """
        Register a new user (driver or admin).
        
        Returns:
        {
            "user_id": 1,
            "email": "driver@example.com",
            "role": "driver",
            "message": "Registration successful"
        }
        or error dict if registration fails
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            return {
                "error": "Email already registered",
                "status": 400
            }
        
        # Create new user
        hashed_password = AuthService.hash_password(password)
        
        new_user = User(
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            phone=phone,
            role=role,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "user_id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role.value,
            "message": f"Registration successful as {role.value}"
        }
    
    @staticmethod
    def login_user(db: Session, email: str, password: str) -> Dict:
        """
        Authenticate user and return JWT token.
        
        Returns:
        {
            "access_token": "...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "driver@example.com",
                "role": "driver"
            }
        }
        or error dict if login fails
        """
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return {
                "error": "Invalid email or password",
                "status": 401
            }
        
        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return {
                "error": "Invalid email or password",
                "status": 401
            }
        
        # Check if active
        if not user.is_active:
            return {
                "error": "Account is inactive",
                "status": 403
            }
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create token
        token_data = AuthService.create_access_token(user.id, user.role)
        
        return {
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
