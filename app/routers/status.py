from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.database import engine, SessionLocal
from app.db.projectStatus.model import ProjectStatus
from app.db.status import schema, crud
from app.db.status.schema import Status
from app.db.task.model import Task
from app.db.projectStatus import model as projectStatus_model

router = APIRouter()

projectStatus_model.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/status/")
def create_status(status: schema.StatusBase, db: Session = Depends(get_db)):
    return crud.create_status(db=db, status=status)

@router.get("/statuses_from_project/{project_id}",response_model=List[schema.Status])
def read_statuses_from_project(project_id: int, db: Session = Depends(get_db)):
    projectStatuses = db.query(projectStatus_model.ProjectStatus).filter(projectStatus_model.ProjectStatus.pid == project_id).all()
    if not projectStatuses:
        raise HTTPException(status_code=404, detail="No statuses found for the given project")
    print("Statuses: ", projectStatuses)
    return [Status.from_orm(projectStatus.status) for projectStatus in projectStatuses]

@router.get("/status/")
def read_statuses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    statuses = crud.get_statuses(db, skip=skip, limit=limit)
    return statuses

@router.get("/status/{status_id}")
def read_status(status_id: int, db: Session = Depends(get_db)):
    db_status = crud.get_status(db, status_id=status_id)
    if db_status is None:
        raise HTTPException(status_code=404, detail="Status not found")
    return db_status



@router.put("/status/{status_id}")
def update_status(status_id: int, status: schema.StatusBase, db: Session = Depends(get_db)):
    db_status = crud.update_status(db, status=status, status_id=status_id)
    return db_status

@router.delete("/status/{status_id}")
def delete_status(status_id: int, db: Session = Depends(get_db)):
    db_status = crud.delete_status(db, status_id=status_id)
    return db_status

