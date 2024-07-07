from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal
from app.db.status import schema, crud
from app.db.status.model import Status
from app.db.task.model import Task

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/status/")
def create_status(status: schema.StatusBase, db: Session = Depends(get_db)):
    return crud.create_status(db=db, status=status)

@router.get("/statuses_from_project/{project_id}")
def read_statuses_from_project(project_id: int, db: Session = Depends(get_db)):
    # Pretpostavka da Task model ima kolonu project_id za povezivanje sa projektom
    tasks = db.query(Task).filter(Task.project == project_id).all()
    status_ids = {task.status for task in tasks}  # Pretpostavka da Task model ima atribut status_id
    statuses = db.query(Status).filter(Status.id.in_(status_ids)).all()  # Pretpostavka da postoji model Status
    print("Statuses: ", statuses)
    if not statuses:
        raise HTTPException(status_code=404, detail="No statuses found for the given project")
    return statuses

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

