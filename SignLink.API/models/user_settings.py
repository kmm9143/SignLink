# DESCRIPTION:  This script defines the SQLAlchemy ORM model for the USER_SETTINGS table.
#               It stores user-specific feature preferences (e.g., speech and webcam settings)
#               and tracks record creation and update timestamps. Each record is linked to
#               a corresponding user in the USER_INFORMATION table via a one-to-one relationship.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). ORM Declarative Mapping. Retrieved October 3, 2025, from https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html
#               [2] SQLAlchemy Documentation. (n.d.). Column and Data Types. Retrieved October 3, 2025, from https://docs.sqlalchemy.org/en/20/core/type_basics.html
#               [3] SQLAlchemy Documentation. (n.d.). Relationships API. Retrieved October 3, 2025, from https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
#               [4] Python Software Foundation. (n.d.). uuid — UUID objects according to RFC 4122. Retrieved October 3, 2025, from https://docs.python.org/3/library/uuid.html

# -------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -------------------------------------------------------------------
from sqlalchemy import Column, Boolean, DateTime, Integer, ForeignKey     # SQLAlchemy column types and foreign key
from sqlalchemy.dialects.postgresql import UUID                           # PostgreSQL UUID data type
from sqlalchemy.sql import func                                           # SQL functions (e.g., current timestamp)
from sqlalchemy.orm import relationship                                   # ORM relationship for table associations
import uuid                                                               # UUID generation for unique primary keys

# -------------------------------------------------------------------
# Step 2: Import base class for SQLAlchemy models
# -------------------------------------------------------------------
from models.base import Base                                              # Base class used for declarative model definitions

# -------------------------------------------------------------------
# Step 3: Define UserSettings model mapped to the USER_SETTINGS table
# -------------------------------------------------------------------
class UserSettings(Base):
    """
    SQLAlchemy model representing user configuration settings.
    Each record corresponds to one user and includes feature preferences
    such as speech and webcam settings, along with timestamps for auditing.
    """

    __tablename__ = "USER_SETTINGS"                                       # Define database table name

    # -------------------------------------------------------------------
    # Step 3a: Define table columns
    # -------------------------------------------------------------------
    ID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)  # Unique identifier (UUID)
    USER_ID = Column(Integer, ForeignKey("USER_INFORMATION.USER_ID"), unique=True, nullable=False)  # Link to user info
    SPEECH_ENABLED = Column(Boolean, default=False, nullable=False)       # Whether speech recognition is enabled
    WEBCAM_ENABLED = Column(Boolean, default=True, nullable=False)        # Whether webcam input is enabled
    CREATED_AT = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)  # Record creation time
    UPDATED_AT = Column(DateTime(timezone=False), onupdate=func.now(), server_default=func.now(), nullable=False)  # Last update time

    # -------------------------------------------------------------------
    # Step 3b: Define ORM relationship to UserInformation
    # -------------------------------------------------------------------
    user = relationship("UserInformation", back_populates="settings")     # One-to-one relationship back to user info
