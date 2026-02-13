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


class UpdateUserRequest(BaseModel):
    """Update user request (admin only)"""
    email: str = None
    full_name: str = None
    phone: str = None
    is_active: bool = None


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str


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

# ADMIN USER MANAGEMENT ENDPOINTS

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    
    Requires: Authorization: Bearer <token> header
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = AuthService.get_user(db, token_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify old password
    if not AuthService.verify_password(request.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Update password
    user.password_hash = AuthService.hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/users")
def list_users(
    skip: int = 0,
    limit: int = 100,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only).
    
    Request params:
    - skip: Number of users to skip (default: 0)
    - limit: Maximum number of users to return (default: 100)
    
    Requires: Authorization: Bearer <token> header with ADMIN role
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check admin role
    if token_data["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view user list"
        )
    
    # Fetch users
    users = db.query(User).offset(skip).limit(limit).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone,
                "role": u.role.value,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "created_at": u.created_at.isoformat() if hasattr(u, 'created_at') else None
            }
            for u in users
        ],
        "total": db.query(User).count(),
        "skip": skip,
        "limit": limit
    }


@router.post("/users")
def create_user_admin(
    request: UserRegisterRequest,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Create a new user (Admin only).
    
    Allows admins to create other users (drivers or admins).
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword",
        "full_name": "User Name",
        "phone": "+1234567890",
        "role": "driver"  # "driver" or "admin"
    }
    
    Requires: Authorization: Bearer <token> header with ADMIN role
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check admin role
    if token_data["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create users"
        )
    
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


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Update user information (Admin only).
    
    Allows admins to edit user details.
    
    Request body (all fields optional):
    {
        "email": "newemail@example.com",
        "full_name": "New Name",
        "phone": "+1234567890",
        "is_active": true
    }
    
    Requires: Authorization: Bearer <token> header with ADMIN role
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check admin role
    if token_data["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can update users"
        )
    
    # Find user
    user = AuthService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if request.email:
        existing = db.query(User).filter(User.email == request.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = request.email
    
    if request.full_name:
        user.full_name = request.full_name
    
    if request.phone:
        user.phone = request.phone
    
    if request.is_active is not None:
        user.is_active = request.is_active
    
    db.commit()
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active
    )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Delete a user (Admin only).
    
    Permanently removes a user from the system.
    
    Requires: Authorization: Bearer <token> header with ADMIN role
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check admin role
    if token_data["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete users"
        )
    
    # Prevent admin from deleting themselves
    if user_id == token_data["user_id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    # Find and delete user
    user = AuthService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"User {user.email} deleted successfully"}


@router.put("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    request: ChangePasswordRequest,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Reset another user's password (Admin only).
    
    Allows admin to set a new password for another user.
    
    Request body:
    {
        "old_password": "not used for admin reset",
        "new_password": "newsecurepassword"
    }
    
    Requires: Authorization: Bearer <token> header with ADMIN role
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    token_data = AuthService.verify_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Check admin role
    if token_data["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can reset user passwords"
        )
    
    # Find user
    user = AuthService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password_hash = AuthService.hash_password(request.new_password)
    db.commit()
    
    return {"message": f"Password reset successfully for user {user.email}"}