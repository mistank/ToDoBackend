from typing import List

from fastapi import HTTPException, APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.taskCategory import crud, schema

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/taskCategories/")
def create_task_category(taskCategory: schema.TaskCategoryBase, db: Session = Depends(get_db)):
    return crud.create_task_category(db=db, taskCategory=taskCategory)

@router.get("/taskCategories/")
def read_taskCategories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),response_model=List[schema.TaskCategory]):
    taskCategories = crud.get_taskCategories(db, skip=skip, limit=limit)
    return taskCategories

@router.get("/taskCategories/{taskCategory_id}")
def read_taskCategory(taskCategory_id: int, db: Session = Depends(get_db)):
    db_taskCategory = crud.get_taskCategory(db, taskCategory_id=taskCategory_id)
    if db_taskCategory is None:
        raise HTTPException(status_code=404, detail="TaskCategory not found")
    return db_taskCategory

@router.put("/taskCategories/{taskCategory_id}")
def update_taskCategory(taskCategory_id: int, taskCategory: schema.TaskCategoryBase, db: Session = Depends(get_db)):
    db_taskCategory = crud.update_taskCategory(db, taskCategory, taskCategory_id)
    return db_taskCategory


