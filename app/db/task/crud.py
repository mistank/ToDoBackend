from sqlalchemy.orm import Session

from app.db.task import model, schema


def create_task(db: Session, task: schema.TaskCreate):
    print(task.dict())
    db_task = model.Task(**task.dict(),status="not started")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_task(db: Session, task_id: int):
    return db.query(model.Task).filter(model.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Task).offset(skip).limit(limit).all()

def update_task(db: Session, task: schema.TaskBase, task_id: int):
    db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
    db_task.name = task.name
    db_task.description = task.description
    db_task.status = task.status
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db, task_id):
    db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
    db.delete(db_task)
    db.commit()
    return db_task
