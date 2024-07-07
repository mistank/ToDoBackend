from sqlalchemy.orm import Session

from app.db.status import schema, model


def create_status(db: Session, status: schema.StatusBase):
    db_status = model.Status(name=status.name)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status


def get_status(db: Session, status_id: int):
    return db.query(model.Status).filter(model.Status.id == status_id).first()

def get_statuses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Status).offset(skip).limit(limit).all()

def update_status(db: Session, status: schema.StatusBase, status_id: int):
    db_status = db.query(model.Status).filter(model.Status.id == status_id).first()
    db_status.name = status.name
    db.commit()
    db.refresh(db_status)
    return db_status

def delete_status(db, status_id):
    db_status = db.query(model.Status).filter(model.Status.id == status_id).first()
    db.delete(db_status)
    db.commit()
    return db_status


def get_status_by_name(db, name):
    return db.query(model.Status).filter(model.Status.name == name).first()