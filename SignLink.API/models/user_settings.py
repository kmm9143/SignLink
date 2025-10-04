from sqlalchemy import Column, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from models.base import Base


class UserSettings(Base):
    __tablename__ = "USER_SETTINGS"

    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    USER_ID = Column(Integer, ForeignKey("USER_INFORMATION.USER_ID"), unique=True, nullable=False)
    SPEECH_ENABLED = Column(Boolean, default=False, nullable=False)
    WEBCAM_ENABLED = Column(Boolean, default=True, nullable=False)
    CREATED_AT = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    UPDATED_AT = Column(DateTime(timezone=False), onupdate=func.now(), server_default=func.now(), nullable=False)

    # relationship back to UserInformation
    user = relationship("UserInformation", back_populates="settings")