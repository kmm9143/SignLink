# DESCRIPTION:  This script defines FastAPI API endpoints for user authentication and account creation.
#               It includes routes for user signup (account registration) and login (credential verification).
#               Passwords are securely hashed using bcrypt via Passlib before storage in the USER_INFORMATION table.
#               The API performs validation for duplicate usernames/emails and enforces secure credential handling.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] FastAPI Documentation. (n.d.). Security and Authentication. Retrieved October 4, 2025, from https://fastapi.tiangolo.com/tutorial/security/
#               [2] Passlib Documentation. (n.d.). CryptContext and bcrypt. Retrieved October 4, 2025, from https://passlib.readthedocs.io/en/stable/lib/passlib.context.html
#               [3] SQLAlchemy Documentation. (n.d.). ORM Query API. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html
#               [4] Pydantic Documentation. (n.d.). EmailStr Type. Retrieved October 4, 2025, from https://docs.pydantic.dev/latest/concepts/types/#emailstr
#               [5] Python Software Foundation. (n.d.). String and Bytes Handling. Retrieved October 4, 2025, from https://docs.python.org/3/library/stdtypes.html#bytes

# -------------------------------------------------------------------
# Step 1: Import required libraries and modules
# -------------------------------------------------------------------
from fastapi import APIRouter, HTTPException, Depends                 # FastAPI tools for routing and error handling
from pydantic import BaseModel, EmailStr                              # Pydantic for input validation (with email type)
from sqlalchemy.orm import Session                                    # SQLAlchemy session for database operations
from passlib.context import CryptContext                              # Passlib for secure password hashing
from database import get_db                                           # Dependency injection for database session
from models.user_information import UserInformation                   # ORM model for user information

# -------------------------------------------------------------------
# Step 2: Configure FastAPI router
# -------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["auth"])                     # Define router with prefix and tag for authentication routes

# -------------------------------------------------------------------
# Step 3: Configure password hashing context
# -------------------------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],                                               # Use bcrypt for password hashing
    deprecated="auto",                                                # Automatically deprecate older hash formats
)

# -------------------------------------------------------------------
# Step 4: Define Pydantic models for request validation
# -------------------------------------------------------------------
class UserCreate(BaseModel):
    """
    Pydantic model for user registration.
    Includes basic user details and password for account creation.
    """
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """
    Pydantic model for user login credentials.
    Used for verifying username and password authentication.
    """
    username: str
    password: str

# -------------------------------------------------------------------
# Step 5: Define API endpoints for authentication
# -------------------------------------------------------------------

# -----------------------------
# (5a) POST /signup — Register a new user
# -----------------------------
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Steps:
    1. Check for existing username or email duplicates.
    2. Truncate password to 72 bytes (bcrypt limitation).
    3. Hash password securely using Passlib.
    4. Insert new user record into USER_INFORMATION table.
    5. Return basic user info (excluding password).
    """

    # Check if username or email already exists
    existing = db.query(UserInformation).filter(
        (UserInformation.USERNAME == user.username) |
        (UserInformation.EMAIL == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Truncate password to 72 bytes (bcrypt max limit)
    truncated_pw_bytes = user.password.encode("utf-8")[:72]

    # Hash password using Passlib
    hashed_pw = pwd_context.hash(truncated_pw_bytes)

    # Create new user record
    new_user = UserInformation(
        FIRST_NAME=user.first_name,
        LAST_NAME=user.last_name,
        EMAIL=user.email,
        USERNAME=user.username,
        PASSWORD=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return sanitized response (exclude password)
    return {
        "id": new_user.USER_ID,
        "username": new_user.USERNAME,
        "first_name": new_user.FIRST_NAME,
        "last_name": new_user.LAST_NAME,
        "email": new_user.EMAIL
    }

# -----------------------------
# (5b) POST /login — Authenticate an existing user
# -----------------------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user by verifying credentials.
    Steps:
    1. Retrieve user record by username.
    2. Verify provided password against stored hash.
    3. Return user profile data on successful login.
    Raises 401 error for invalid credentials.
    """
    db_user = db.query(UserInformation).filter(UserInformation.USERNAME == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.PASSWORD):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "id": db_user.USER_ID,
        "username": db_user.USERNAME,
        "first_name": db_user.FIRST_NAME,
        "last_name": db_user.LAST_NAME,
        "email": db_user.EMAIL
    }