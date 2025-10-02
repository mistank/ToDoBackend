from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.taskCategory import model, schema
from app.exceptions import handle_database_error, handle_not_found


def create_task_category(db: Session, task_category: schema.TaskCategoryBase):
    try:
        db_task_category = model.TaskCategory(**task_category.dict())
        db.add(db_task_category)
        db.commit()
        db.refresh(db_task_category)
        return db_task_category
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Create task category", detail="Task category name already exists")
        else:
            handle_database_error(e, "Create task category")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create task category")

def get_taskCategory(db: Session, task_category_id: int):
    try:
        return db.query(model.TaskCategory).filter(model.TaskCategory.id == task_category_id).first()
    except Exception as e:
        handle_database_error(e, "Get task category")

def get_taskCategories(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.TaskCategory).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get task categories")

def update_taskCategory(db: Session, task_category: schema.TaskCategoryBase, task_category_id: int):
    try:
        db_task_category = db.query(model.TaskCategory).filter(model.TaskCategory.id == task_category_id).first()
        if not db_task_category:
            handle_not_found("Task category", task_category_id)

        db_task_category.name = task_category.name
        db.commit()
        db.refresh(db_task_category)
        return db_task_category
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Update task category", detail="Task category name already exists")
        else:
            handle_database_error(e, "Update task category")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update task category")

def delete_taskCategory(db, task_category_id):
    try:
        db_task_category = db.query(model.TaskCategory).filter(model.TaskCategory.id == task_category_id).first()
        if not db_task_category:
            handle_not_found("Task category", task_category_id)

        db.delete(db_task_category)
        db.commit()
        return db_task_category
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete task category")


