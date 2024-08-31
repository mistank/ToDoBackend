from datetime import datetime

import pytz
from sqlalchemy.orm import Session

from app.db.task import model, schema
from app.db.status import model as status_model
from app.db.task.schema import Task


def create_task(db: Session, task: schema.TaskCreate, response_model=schema.Task):
    db_task = model.Task(**task.dict())
    # print("Task that is sent: ", db_task.deadline)
    # #db_task.deadline = datetime.fromisoformat(str(db_task.deadline)).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Belgrade')).isoformat()
    # if db_task.deadline:
    #     local_tz = pytz.timezone('Europe/Belgrade')
    #     utc_dt = datetime.fromisoformat(str(db_task.deadline)).replace(tzinfo=pytz.utc)
    #     local_dt = utc_dt.astimezone(local_tz)
    #     db_task.deadline = local_dt.isoformat()
    # print("Task that is sent: ", db_task.deadline)
    # print("Task that is sent: ", db_task)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return Task.from_orm(db_task)

#datetime.fromisoformat(value).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Belgrade')).isoformat()
def get_task(db: Session, task_id: int):
    return db.query(model.Task).filter(model.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Task).offset(skip).limit(limit).all()


def update_task(db: Session, task: schema.TaskBase, task_id: int, response_model=schema.Task):
    db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
    print("Task that is pulled: ", db_task)
    print("Task that is sent: ", task)
    db_task.name = task.name
    db_task.description = task.description
    db_task.taskCategory_id = task.taskCategory_id
    db_task.deadline = task.deadline
    db_task.priority = task.priority
    db.commit()
    db.refresh(db_task)
    return Task.from_orm(db_task)


def delete_task(db, task_id):
    db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
    db.delete(db_task)
    db.commit()
    return db_task


def update_task_status(db, task_id, status_id):
    db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
    db_status = db.query(status_model.Status).filter(status_model.Status.id == status_id).first()
    db_task.status_id = status_id
    db.commit()
    db.refresh(db_task)
    return db_task
