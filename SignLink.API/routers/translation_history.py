from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from typing import Optional
from crud import log_translation, get_translation_history, clear_translation_history
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/translations", tags=["user_translation_history"])

class TranslationCreate(BaseModel):
    user_id: int
    input_type: str
    filename: Optional[str] = None
    recognized_text: str
    
@router.post("/")
def create_translation(entry: TranslationCreate, db: Session = Depends(get_db)):
    try:
        return log_translation(db, entry.user_id, entry.input_type, entry.recognized_text, entry.filename)
    except SQLAlchemyError as e:
        print("❌ SQLAlchemyError:", str(e))  # <-- add this
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except ValueError as e:
        print("❌ ValueError:", str(e))  # <-- add this
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("❌ Unexpected error:", str(e))  # <-- add this
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))


@router.get("/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db), limit: int = Query(10, gt=0)):
    try:
        return get_translation_history(db, user_id=user_id, limit=limit)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

@router.delete("/{user_id}")
def delete_user_history(user_id: int, db: Session = Depends(get_db)):
    try:
        return clear_translation_history(db, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))