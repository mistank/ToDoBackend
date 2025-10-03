from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.role import schema, model
from app.exceptions import handle_database_error, handle_not_found


def create_role(db: Session, role: schema.Role):
    try:
        db_role = model.Role(name=role.name)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Create role", detail="Role name already exists")
        else:
            handle_database_error(e, "Create role")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create role")

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.Role).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get roles")

def get_role(db: Session, role_id: int):
    try:
        return db.query(model.Role).filter(model.Role.id == role_id).first()
    except Exception as e:
        handle_database_error(e, "Get role")

def update_role(db: Session, role: schema.Role, role_id: int):
    try:
        db_role = db.query(model.Role).filter(model.Role.id == role_id).first()
        if not db_role:
            handle_not_found("Role", role_id)

        db_role.name = role.name
        db.commit()
        db.refresh(db_role)
        return db_role
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Update role", detail="Role name already exists")
        else:
            handle_database_error(e, "Update role")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update role")

def delete_role(db: Session, role_id: int):
    try:
        db_role = db.query(model.Role).filter(model.Role.id == role_id).first()
        if not db_role:
            handle_not_found("Role", role_id)

        db.delete(db_role)
        db.commit()
        return db_role
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete role")

