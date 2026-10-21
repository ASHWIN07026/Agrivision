"""
SQLAlchemy ORM models for AgriVision.
"""
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    module = Column(String, nullable=False)          # "disease" | "yield" | "market"
    input_data = Column(Text, nullable=True)         # JSON string of inputs
    result = Column(Text, nullable=True)             # JSON string of output
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
