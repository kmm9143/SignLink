# DESCRIPTION:  This script defines the SQLAlchemy ORM model for the USER_TRANSLATION_HISTORY table.
#               It represents user translation events recorded in the database, including
#               input type, recognized text, and creation timestamp. Each record links back
#               to a user in the USER_INFORMATION table.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). ORM Declarative Mapping. Retrieved October 25, 2025, from https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html
#               [2] SQLAlchemy Documentation. (n.d.). Column and Data Types. Retrieved October 25, 2025, from https://docs.sqlalchemy.org/en/20/core/type_basics.html
#               [3] SQLAlchemy Documentation. (n.d.). Relationships API. Retrieved October 25, 2025, from https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
#               [4] Python Software Foundation. (n.d.). uuid — UUID objects according to RFC 4122. Retrieved October 25, 2025, from https://docs.python.org/3/library/uuid.html

# -------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -------------------------------------------------------------------
from sqlalchemy import Column, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# -------------------------------------------------------------------
# Step 2: Import base class for SQLAlchemy models
# -------------------------------------------------------------------
from models.base import Base  # Declarative base used across models

# -------------------------------------------------------------------
# Step 3: Define TranslationHistory model mapped to TRANSLATION_HISTORY table
# -------------------------------------------------------------------
class UserTranslationHistory(Base):
    """
    SQLAlchemy model representing user translation log entries.
    Each record stores the recognized text, input type, timestamp,
    and user association.
    """

    __tablename__ = "USER_TRANSLATION_HISTORY"  # Define table name

    # -------------------------------------------------------------------
    # Step 3a: Define table columns
    # -------------------------------------------------------------------
    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    USER_ID = Column(BigInteger, ForeignKey("USER_INFORMATION.USER_ID"), nullable=False)
    INPUT_TYPE = Column(Text, nullable=False)
    FILENAME = Column(Text, nullable=True)
    RECOGNIZED_TEXT = Column(Text, nullable=False)
    CREATED_AT = Column(DateTime, nullable=False, default=datetime.utcnow)

    # -------------------------------------------------------------------
    # Step 3b: Define ORM relationship to UserInformation
    # -------------------------------------------------------------------
    user = relationship("UserInformation", back_populates="user_translation_history")