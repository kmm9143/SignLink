# DESCRIPTION:  This script defines the SQLAlchemy ORM model for the USER_INFORMATION table.
#               It stores user account details including username, name, email, and password (hashed),
#               along with timestamps for record creation and updates. The model also establishes a
#               one-to-one relationship with the USER_SETTINGS table to manage user-specific preferences.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). ORM Declarative Mapping. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html
#               [2] SQLAlchemy Documentation. (n.d.). Column and Data Types. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/core/type_basics.html
#               [3] SQLAlchemy Documentation. (n.d.). Relationships API. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/orm/relationship_api.html
#               [4] Python Software Foundation. (n.d.). hashlib — Secure hashes and message digests. Retrieved October 4, 2025, from https://docs.python.org/3/library/hashlib.html

# -------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -------------------------------------------------------------------
from sqlalchemy import Column, String, DateTime, Integer                   # SQLAlchemy column and type classes
from sqlalchemy.sql import func                                            # SQL functions (e.g., timestamps)
from sqlalchemy.orm import relationship                                    # ORM relationship management

# -------------------------------------------------------------------
# Step 2: Import base class for SQLAlchemy models
# -------------------------------------------------------------------
from models.base import Base                                               # Base class for declarative models

# -------------------------------------------------------------------
# Step 3: Define UserInformation model mapped to the USER_INFORMATION table
# -------------------------------------------------------------------
class UserInformation(Base):
    """
    SQLAlchemy model representing user account information.
    Each record stores the user's credentials and personal details,
    and links to a corresponding UserSettings record for preferences.
    """

    __tablename__ = "USER_INFORMATION"                                     # Define the database table name

    # -------------------------------------------------------------------
    # Step 3a: Define table columns
    # -------------------------------------------------------------------
    USER_ID = Column(Integer, primary_key=True, autoincrement=True)        # Unique user identifier
    USERNAME = Column(String, unique=True, nullable=False)                 # Unique username for login
    FIRST_NAME = Column(String, nullable=True)                             # User’s first name (optional)
    LAST_NAME = Column(String, nullable=True)                              # User’s last name (optional)
    EMAIL = Column(String, unique=True, nullable=False)                    # Unique email address
    PASSWORD = Column(String, nullable=False)                              # Hashed user password
    CREATED_AT = Column(DateTime(timezone=False), server_default=func.now(), nullable=False)  # Record creation time
    UPDATED_AT = Column(DateTime(timezone=False), onupdate=func.now(), server_default=func.now(), nullable=False)  # Last update time

    # -------------------------------------------------------------------
    # Step 3b: Define ORM relationship to UserSettings
    # -------------------------------------------------------------------
    settings = relationship("UserSettings", back_populates="user", uselist=False)  # One-to-one relationship with UserSettings