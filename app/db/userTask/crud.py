from app import db
from app.db.userTask.model import UserTask
from sqlalchemy.orm import Session, joinedload


def assign_user_task(user_id: int, task_id: int, db: Session):
    user_task = UserTask(uid=user_id, tid=task_id)
    db.add(user_task)
    db.commit()
    return user_task

def get_user_task(user_id: int, task_id: int, db: Session):
    return db.query(UserTask).filter(UserTask.uid == user_id, UserTask.tid == task_id).first()
def get_user_tasks(user_id: int, db: Session):
    return db.query(UserTask).filter(UserTask.user_id == user_id).all()


def get_task_users(task_id: int, db: Session):
    return db.query(UserTask).filter(UserTask.task_id == task_id).all()


def get_users_for_task(db, task_id):
    user_tasks = db.query(UserTask).options(joinedload(UserTask.user)).filter(UserTask.tid == task_id).all()
    users = [user_task.user for user_task in user_tasks]
    return users


def remove_user_from_task(db, user_id, task_id):
    user_task = db.query(UserTask).filter(UserTask.uid == user_id, UserTask.tid == task_id).first()
    db.delete(user_task)
    db.commit()
    return user_task