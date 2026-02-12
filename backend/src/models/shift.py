from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import relationship

from src.database import Base


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    earnings = Column(Float, default=0.0)
    predicted_earnings = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

    worker = relationship("Worker", back_populates="shifts")
