from datetime import datetime

import pytz
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.task import model, schema
from app.db.status import model as status_model
from app.db.task.schema import Task
from app.exceptions import handle_database_error, handle_not_found


def create_task(db: Session, task: schema.TaskCreate, response_model=schema.Task):
    try:
        db_task = model.Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return Task.from_orm(db_task)
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Create task")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create task")

#datetime.fromisoformat(value).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Belgrade')).isoformat()
def get_task(db: Session, task_id: int):
    try:
        return db.query(model.Task).filter(model.Task.id == task_id).first()
    except Exception as e:
        handle_database_error(e, "Get task")


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.Task).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get tasks")


def update_task(db: Session, task: schema.TaskBase, task_id: int, response_model=schema.Task):
    try:
        db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
        if not db_task:
            handle_not_found("Task", task_id)

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
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Update task")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update task")


def delete_task(db, task_id):
    try:
        db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
        if not db_task:
            handle_not_found("Task", task_id)

        db.delete(db_task)
        db.commit()
        return db_task
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete task")


def update_task_status(db, task_id, status_id):
    try:
        db_task = db.query(model.Task).filter(model.Task.id == task_id).first()
        if not db_task:
            handle_not_found("Task", task_id)

        db_status = db.query(status_model.Status).filter(status_model.Status.id == status_id).first()
        if not db_status:
            handle_not_found("Status", status_id)

        db_task.status_id = status_id
        db.commit()
        db.refresh(db_task)
        return db_task
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Update task status")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update task status")
