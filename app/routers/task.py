from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.database import engine, SessionLocal
from app.db.status.schema import Status
from app.db.task import model, crud, schema
from app.db.task.schema import Task
from app.db.taskCategory import model as taskCat_model
from app.db.status import model as status_model
from app.db.userTask import model as userTask_model
from app.db.userTask import crud as userTask_crud
from app.db.userTask import schema as userTask_schema
from app.db.user import crud as user_crud

model.Base.metadata.create_all(bind=engine)
taskCat_model.Base.metadata.create_all(bind=engine)
status_model.Base.metadata.create_all(bind=engine)
userTask_model.Base.metadata.create_all(bind=engine)


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tasks/")
def create_task(task: schema.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db=db, task=task)


@router.post("/tasks/add_user/", response_model=userTask_schema.UserTask)
def add_user_to_task(task_id: int, user_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_user = user_crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user_task = userTask_crud.get_user_task(user_id,task_id, db)
    if db_user_task:
        raise HTTPException(status_code=400, detail="User already assigned to the task")
    return userTask_crud.assign_user_task(db=db, task_id=task_id, user_id=user_id)


@router.get("/tasks/")
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),response_model=List[schema.Task]):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return [Task.from_orm(task) for task in tasks]

@router.get("/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task



# @router.get("/tasks_from_project/{project_id}")
# def read_tasks_from_project(project_id: int, db: Session = Depends(get_db)):
#     tasks = db.query(model.Task).options(
#         joinedload(model.Task.project_rel),
#         joinedload(model.Task.taskCategory_rel),
#         joinedload(model.Task.status_rel)
#     ).filter(model.Task.project == project_id).all()
#     if not tasks:
#         raise HTTPException(status_code=404, detail="No tasks found for the given project")
#     print("Tasks: ", tasks)#     return tasks


@router.get("/tasks_from_project/{project_id}", response_model=List[schema.Task])
def read_tasks_from_project(project_id: int, db: Session = Depends(get_db)):
    tasks = db.query(model.Task).filter(model.Task.project_id == project_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for the given project")
    # Konvertovanje ORM objekata u Pydantic modele
    return [Task.from_orm(task) for task in tasks]

@router.get("/tasks_with_status/{status_id}")
def read_tasks_with_status(status_id: int, db: Session = Depends(get_db)):
    tasks = db.query(model.Task).filter(model.Task.status == status_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for the given status")
    return tasks

@router.put("/tasks/{task_id}")
def update_task(task_id: int, task: schema.TaskBase, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task=task, task_id=task_id)
    return db_task

@router.patch("/change_task_status/{task_id}")
def update_task_status(task_id: int, status: Status, db: Session = Depends(get_db)):
    print("Task ID: ", task_id)
    print("Status ID: ", status.id)
    db_task = crud.update_task_status(db, task_id=task_id, status_id=status.id)
    return db_task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.delete_task(db, task_id=task_id)
    return db_task


