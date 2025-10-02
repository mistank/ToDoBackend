from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.projectUserRole import model, schema
from app.db.projectUserRole.model import ProjectUserRole
from app.exceptions import handle_database_error, handle_not_found

def get_roles_by_pid(db: Session, pid: int):
    try:
        return db.query(model.ProjectUserRole).filter(model.ProjectUserRole.project_id == pid).all()
    except Exception as e:
        handle_database_error(e, "Get roles by project")

#vrati sve projekte na kojima je korisnik
def get_roles_by_user(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.ProjectUserRole).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get roles by user")


def create_role(db: Session, projectUserRole: schema.ProjectUserRoleBase):
    try:
        db_projectUserRole = model.ProjectUserRole(uid=projectUserRole.uid, pid=projectUserRole.pid, rid=projectUserRole.rid)
        db.add(db_projectUserRole)
        db.commit()
        db.refresh(db_projectUserRole)
        return db_projectUserRole
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Create project user role", detail="User role already exists for this project")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create project user role")


def add_user_to_project(db, project_id, user_id, role_id):
    try:
        db_projectUserRole = model.ProjectUserRole(uid=user_id, pid=project_id, rid=role_id)
        db.add(db_projectUserRole)
        db.commit()
        db.refresh(db_projectUserRole)
        return db_projectUserRole
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Add user to project", detail="User already added to project")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Add user to project")

def get_user_project(uid, project_id, db):
    try:
        return db.query(ProjectUserRole).filter(ProjectUserRole.uid == uid, ProjectUserRole.pid == project_id).first()
    except Exception as e:
        handle_database_error(e, "Get user project")


def remove_user_from_project(db, project_id, user_id):
    try:
        db_projectUserRole = db.query(ProjectUserRole).filter(ProjectUserRole.pid == project_id, ProjectUserRole.uid == user_id).first()
        if not db_projectUserRole:
            handle_not_found("Project user role", f"project_id={project_id}, user_id={user_id}")

        db.delete(db_projectUserRole)
        db.commit()
        return db_projectUserRole
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Remove user from project")


def update_user_role(db, project_id, user_id, role_id):
    try:
        db_projectUserRole = db.query(ProjectUserRole).filter(ProjectUserRole.pid == project_id, ProjectUserRole.uid == user_id).first()
        if not db_projectUserRole:
            handle_not_found("Project user role", f"project_id={project_id}, user_id={user_id}")

        db_projectUserRole.rid = role_id
        db.commit()
        db.refresh(db_projectUserRole)
        return db_projectUserRole
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Update user role")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update user role")