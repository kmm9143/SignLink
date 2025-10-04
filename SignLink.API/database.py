# DESCRIPTION:  This script configures the database connection and session management for the application.
#               It loads environment variables, creates a SQLAlchemy engine using the DATABASE_URL,
#               and defines a session factory for database transactions. The `get_db()` function provides
#               a dependency-injected database session for FastAPI routes, ensuring proper connection
#               handling and cleanup after each request.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). Engine Configuration. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/core/engines.html
#               [2] SQLAlchemy Documentation. (n.d.). Session Basics. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/orm/session_basics.html
#               [3] FastAPI Documentation. (n.d.). Dependencies with yield. Retrieved October 4, 2025, from https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
#               [4] python-dotenv Documentation. (n.d.). load_dotenv Function. Retrieved October 4, 2025, from https://saurabh-kumar.com/python-dotenv/
#               [5] Python Software Foundation. (n.d.). os — Miscellaneous operating system interfaces. Retrieved October 4, 2025, from https://docs.python.org/3/library/os.html

# -------------------------------------------------------------------
# Step 1: Import required modules and dependencies
# -------------------------------------------------------------------
from models.base import Base                          # Import the declarative base class for ORM models
from sqlalchemy import create_engine                  # SQLAlchemy function to create a database engine
from sqlalchemy.orm import sessionmaker               # Factory for creating database session objects
import os                                              # Used for accessing environment variables
from dotenv import load_dotenv                         # Utility to load environment variables from a .env file

# -------------------------------------------------------------------
# Step 2: Load environment variables
# -------------------------------------------------------------------
load_dotenv()                                          # Load environment variables from .env file into system environment

# -------------------------------------------------------------------
# Step 3: Retrieve database connection URL from environment
# -------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")               # Fetch the DATABASE_URL variable from environment
if not DATABASE_URL:                                   # Check if DATABASE_URL is not set
    raise ValueError("DATABASE_URL not set in environment")  # Raise an error if no database URL is found

# -------------------------------------------------------------------
# Step 4: Create SQLAlchemy engine
# -------------------------------------------------------------------
engine = create_engine(DATABASE_URL)                   # Initialize database engine using the provided URL

# -------------------------------------------------------------------
# Step 5: Create session factory for database interactions
# -------------------------------------------------------------------
SessionLocal = sessionmaker(                           # Define session factory for managing database sessions
    autocommit=False,                                  # Disable autocommit (transactions must be manually committed)
    autoflush=False,                                   # Disable autoflush for more explicit session control
    bind=engine                                        # Bind the session factory to the created engine
)

# -------------------------------------------------------------------
# Step 6: Define dependency function for FastAPI routes
# -------------------------------------------------------------------
def get_db():
    """
    Provides a database session for API endpoints.
    Ensures session is properly closed after use.
    """
    db = SessionLocal()                                # Create a new database session instance
    try:
        yield db                                       # Yield the session for use in a request context
    finally:
        db.close()                                     # Ensure the session is closed after the request completes