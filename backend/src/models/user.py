"""
User Authentication Model

Represents system users (Drivers and Administrators) with role-based access.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime

from src.database import Base


class UserRole(str, PyEnum):
    """User role enumeration"""
    DRIVER = "driver"
    ADMIN = "admin"


class User(Base):
    """
    User ORM Model - System authentication and authorization.
    
    Supports two roles:
    - Driver: Views recommendations, commits to shifts, sees earnings/guarantees
    - Admin: Manages datasets, adjusts parameters, reviews analytics
    
    Database Table: users
    Relationships:
        One User can have many shifts (if driver)
        One User can manage many parameter settings (if admin)
    """
    __tablename__ = "users"
    
    # PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)
    
    # AUTHENTICATION
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)  # Use bcrypt hashing
    
    # PROFILE
    full_name = Column(String(128), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # ROLE & PERMISSIONS
    role = Column(Enum(UserRole), default=UserRole.DRIVER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # TIMESTAMPS
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # RELATIONSHIPS
    # Drivers can have multiple shifts
    shifts = relationship("Shift", back_populates="driver", foreign_keys="Shift.driver_id")
    
    # Admins can create system settings
    admin_settings = relationship("AdminSettings", back_populates="admin")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"


class AdminSettings(Base):
    """
    Admin-configurable system parameters.
    
    Allows administrators to adjust:
    - Guarantee threshold
    - Minimum eligibility requirements
    - Model parameters
    - System settings
    """
    __tablename__ = "admin_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to admin user
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    admin = relationship("User", back_populates="admin_settings")
    
    # Settings parameters
    setting_key = Column(String(128), nullable=False, unique=True)
    setting_value = Column(String(512), nullable=False)
    setting_type = Column(String(50), default="string")  # string, float, int, bool
    description = Column(String(256), nullable=True)
    
    # Tracking
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Examples of settings:
    # GUARANTEE_THRESHOLD: 0.90
    # MIN_ACTIVE_HOURS: 20.0
    # MIN_ACCEPTANCE_RATE: 0.95
    # MAX_CANCELLATION_RATE: 0.05
