from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base
import datetime
import enum
import uuid

Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AudioJob(Base):
    __tablename__ = "audio_jobs"
    
    # Generate a unique ID for each uploaded audio file
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)