from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models.user_information import UserInformation

router = APIRouter()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

# Signup model
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # check if username/email exists
    existing = db.query(UserInformation).filter(
        (UserInformation.USERNAME == user.username) |
        (UserInformation.EMAIL == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # truncate password to 72 bytes for bcrypt
    truncated_pw_bytes = user.password.encode("utf-8")[:72]
    
    # hash using passlib (accepts bytes)
    hashed_pw = pwd_context.hash(truncated_pw_bytes)

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
    return {
        "id": new_user.USER_ID,
        "username": new_user.USERNAME,
        "first_name": new_user.FIRST_NAME,
        "last_name": new_user.LAST_NAME,
        "email": new_user.EMAIL
    }

# Login model
class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
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
