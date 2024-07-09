from sqlalchemy.orm import Session
from app.db.taskCategory import model, schema


def create_task_category(db: Session, task_category: schema.TaskCategoryBase):
    db_task_category = model.TaskCategory(**task_category.dict())
    db.add(db_task_category)
    db.commit()
    db.refresh(db_task_category)
    return db_task_category

def get_taskCategory(db: Session, task_category_id: int):
    return db.query(model.TaskCategory).filter(model.TaskCategory.id == task_category_id).first()

def get_taskCategories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.TaskCategory).offset(skip).limit(limit).all()

def update_taskCategory(db: Session, task_category: schema.TaskCategoryBase, task_category_id: int):
    db_task_category = db.query(model.TaskCategory).filter(model.TaskCategory.id == task_category_id).first()
    db_task_category.name = task_category.name
    db.commit()
    db.refresh(db_task_category)
    return db_task_category

def delete_taskCategory(db, task_category_id):
    db_task_category = db.query(model.TaskCategory).filter(model.TaskCategory.id == task_category_id).first()
    db.delete(db_task_category)
    db.commit()
    return db_task_category


