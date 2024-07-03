from sqlalchemy.orm import Session

from app.db.permission import model, schema
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_role(db: Session, permission_id: int):
    return db.query(model.Permission).filter(model.Permission.id == permission_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Permission).offset(skip).limit(limit).all()


def create_role(db: Session, permission: schema.PermissionBase):
    db_permission = model.Permission(name=permission.name)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission
