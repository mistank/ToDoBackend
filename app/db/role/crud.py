from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.role import schema, model


def create_role(db: Session, role: schema.RoleCreate):
    try:
        db_role = model.Role(name=role.name, description=role.description)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError as e:
        db.rollback()
        error_code = e.orig.args[0]  # Extract the error code
        print(type(error_code))
        #1062 is the error code for duplicate entry
        if error_code == 1062:
            raise HTTPException(status_code=400, detail="Role name already exists")

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Role).offset(skip).limit(limit).all()

def get_role(db: Session, role_id: int):
    return db.query(model.Role).filter(model.Role.id == role_id).first()

def update_role(db: Session, role: schema.Role, role_id: int):
    db_role = db.query(model.Role).filter(model.Role.id == role_id).first()
    db_role.name = role.name
    db_role.description = role.description
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    db_role = db.query(model.Role).filter(model.Role.id == role_id).first()
    db.delete(db_role)
    db.commit()
    return db_role

