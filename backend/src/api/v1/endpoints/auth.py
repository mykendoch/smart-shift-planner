"""
Authentication API Endpoints

Routes for user registration, login, and profile management.
Supports both Driver and Administrator roles.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from src.database import get_db
from src.services.auth import AuthService
from src.models.user import UserRole, User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# REQUEST/RESPONSE SCHEMAS
class UserRegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str  # Min 8 chars, should be enforced on frontend
    full_name: str
    phone: str = None
    role: str = "driver"  # "driver" or "admin"


class UserLoginRequest(BaseModel):
    """User login request"""
    email: str
    password: str


class UserResponse(BaseModel):
    """User profile response"""
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str
    user: UserResponse


# ENDPOINTS
@router.post("/register", response_model=UserResponse)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user (Driver or Administrator).
    
    Request body:
    {
        "email": "driver@example.com",
        "password": "securepassword",
        "full_name": "John Doe",
        "phone": "+1234567890",
        "role": "driver"  # "driver" or "admin"
    }
    
    Returns:
    {
        "id": 1,
        "email": "driver@example.com",
        "full_name": "John Doe",
        "role": "driver",
        "is_active": true
    }
    """
    # Validate role
    if request.role not in ["driver", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'driver' or 'admin'"
        )
    
    # Register user
    role = UserRole.DRIVER if request.role == "driver" else UserRole.ADMIN
    result = AuthService.register_user(
        db=db,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        phone=request.phone,
        role=role
    )
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status", 400),
            detail=result["error"]
        )
    
    # Fetch and return user
    user = AuthService.get_user(db, result["user_id"])
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active
    )


@router.post("/login", response_model=TokenResponse)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    Request body:
    {
        "email": "driver@example.com",
        "password": "securepassword"
    }
    
    Returns:
    {
        "access_token": "eyJhbGc...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "email": "driver@example.com",
            "full_name": "John Doe",
            "role": "driver",
            "is_active": true
        }
    }
    """
    result = AuthService.login_user(db, request.email, request.password)
    
    if "error" in result:
        raise HTTPException(
            status_code=result.get("status", 401),
            detail=result["error"]
        )
    
    # Fetch user for response
    user = AuthService.get_user_by_email(db, request.email)
    
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile.
    
    Requires: Authorization: Bearer <token> header
    
    Returns user profile information.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication token"
        )
    
    # Verify token
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    user = AuthService.get_user(db, token_data["user_id"])
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active
    )
