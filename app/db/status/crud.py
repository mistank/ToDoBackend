from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.status import schema, model
from app.exceptions import handle_database_error, handle_not_found


def create_status(db: Session, status: schema.StatusBase):
    try:
        db_status = model.Status(name=status.name)
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        return db_status
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Create status", detail="Status name already exists")
        else:
            handle_database_error(e, "Create status")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create status")


def get_status(db: Session, status_id: int):
    try:
        return db.query(model.Status).filter(model.Status.id == status_id).first()
    except Exception as e:
        handle_database_error(e, "Get status")

def get_statuses(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.Status).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get statuses")

def update_status(db: Session, status: schema.StatusBase, status_id: int):
    try:
        db_status = db.query(model.Status).filter(model.Status.id == status_id).first()
        if not db_status:
            handle_not_found("Status", status_id)

        db_status.name = status.name
        db.commit()
        db.refresh(db_status)
        return db_status
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Update status", detail="Status name already exists")
        else:
            handle_database_error(e, "Update status")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update status")

def delete_status(db, status_id):
    try:
        db_status = db.query(model.Status).filter(model.Status.id == status_id).first()
        if not db_status:
            handle_not_found("Status", status_id)

        db.delete(db_status)
        db.commit()
        return db_status
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete status")


def get_status_by_name(db, name):
    try:
        return db.query(model.Status).filter(model.Status.name == name).first()
    except Exception as e:
        handle_database_error(e, "Get status by name")