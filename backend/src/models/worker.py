from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from src.database import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=128), nullable=False, index=True)
    email = Column(String(length=256), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    shifts = relationship("Shift", back_populates="worker")

