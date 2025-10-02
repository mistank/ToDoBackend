from app import db
from app.db.userTask.model import UserTask
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.exceptions import handle_database_error, handle_not_found


def assign_user_task(user_id: int, task_id: int, db: Session):
    try:
        user_task = UserTask(uid=user_id, tid=task_id)
        db.add(user_task)
        db.commit()
        return user_task
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Assign user task", detail="User already assigned to this task")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Assign user task")

def get_user_task(user_id: int, task_id: int, db: Session):
    try:
        return db.query(UserTask).filter(UserTask.uid == user_id, UserTask.tid == task_id).first()
    except Exception as e:
        handle_database_error(e, "Get user task")

def get_tasks_assigned_to_user(user_id: int,skip: int, limit:int, db: Session):
    try:
        user_tasks = db.query(UserTask).filter(UserTask.uid == user_id).offset(skip).limit(limit).all()
        tasks = [user_task.task for user_task in user_tasks]
        return tasks
    except Exception as e:
        handle_database_error(e, "Get tasks assigned to user")

def get_task_users(task_id: int, db: Session):
    try:
        return db.query(UserTask).filter(UserTask.task_id == task_id).all()
    except Exception as e:
        handle_database_error(e, "Get task users")


def get_users_for_task(db, task_id):
    try:
        user_tasks = db.query(UserTask).options(joinedload(UserTask.user)).filter(UserTask.tid == task_id).all()
        users = [user_task.user for user_task in user_tasks]
        return users
    except Exception as e:
        handle_database_error(e, "Get users for task")


def remove_user_from_task(db, user_id, task_id):
    try:
        user_task = db.query(UserTask).filter(UserTask.uid == user_id, UserTask.tid == task_id).first()
        if not user_task:
            handle_not_found("User task", f"user_id={user_id}, task_id={task_id}")

        db.delete(user_task)
        db.commit()
        return user_task
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Remove user from task")