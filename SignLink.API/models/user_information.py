from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from models.base import Base


class UserInformation(Base):
    __tablename__ = "USER_INFORMATION"

    USER_ID = Column(Integer, primary_key=True, autoincrement=True)
    USERNAME = Column(String, unique=True, nullable=False)
    FIRST_NAME = Column(String, nullable=True)
    LAST_NAME = Column(String, nullable=True)
    EMAIL = Column(String, unique=True, nullable=False)
    PASSWORD = Column(String, nullable=False)  # hashed password
    CREATED_AT = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)
    UPDATED_AT = Column(DateTime(timezone=False), onupdate=func.now(), server_default=func.now(), nullable=False)

    # relationship to UserSettings (one-to-one)
    settings = relationship("UserSettings", back_populates="user", uselist=False)