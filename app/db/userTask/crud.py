from app import db
from app.db.userTask.model import UserTask
from sqlalchemy.orm import Session



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

