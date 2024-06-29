from sqlalchemy.orm import Session

from app.db.role import model, schema
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_role(db: Session, role_id: int):
    return db.query(model.Role).filter(model.Role.id == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: schema.RoleBase):
    db_role = model.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role
