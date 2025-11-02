from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from typing import List
from uuid import UUID
from crud import log_translation, get_translation_history, clear_translation_history, delete_translation_logs
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/translations", tags=["user_translation_history"])

class TranslationCreate(BaseModel):
    user_id: int
    input_type: str
    filename: str | None = None
    recognized_text: str

class DeleteLogsRequest(BaseModel):
    log_ids: List[UUID]  # updated to UUID

@router.post("/")
def create_translation(entry: TranslationCreate, db: Session = Depends(get_db)):
    try:
        return log_translation(db, entry.user_id, entry.input_type, entry.recognized_text, entry.filename)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    try:
        return get_translation_history(db, user_id=user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{user_id}/logs")
def delete_logs(user_id: int, body: DeleteLogsRequest = Body(...), db: Session = Depends(get_db)):
    if not body.log_ids:
        raise HTTPException(status_code=400, detail="No log_ids provided")
    try:
        return delete_translation_logs(db, user_id, body.log_ids)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{user_id}/all")
def delete_all_logs(user_id: int, db: Session = Depends(get_db)):
    try:
        return clear_translation_history(db, user_id)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")