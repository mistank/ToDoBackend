from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.projectUserRole import model, schema
from app.db.projectUserRole.model import ProjectUserRole

#tabela namenjena onim korisnicima koje se nalaze na nekom projektu, ali nisu vlasnici projekta
#koristicemo je kada budemo dodavali funkcionalnost dodavanja ljudi na projekat (kolaboratora)

# def get_role_by_rid(db: Session, rid: int):
#     return db.query(model.ProjectUserRole).filter(model.ProjectUserRole.id == rid).first()

def get_roles_by_pid(db: Session, pid: int):
    return db.query(model.ProjectUserRole).filter(model.ProjectUserRole.project_id == pid).all()

#vrati sve projekte na kojima je korisnik
def get_roles_by_user(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.ProjectUserRole).offset(skip).limit(limit).all()


def create_role(db: Session, projectUserRole: schema.ProjectUserRoleBase):
    db_projectUserRole = model.ProjectUserRole(uid=projectUserRole.uid, pid=projectUserRole.pid, rid=projectUserRole.rid)
    db.add(db_projectUserRole)
    db.commit()
    db.refresh(db_projectUserRole)
    return db_projectUserRole


def add_user_to_project(db, project_id, user_id, role_id):
    try:
        db_projectUserRole = model.ProjectUserRole(uid=user_id, pid=project_id, rid=role_id)
        db.add(db_projectUserRole)
        db.commit()
        db.refresh(db_projectUserRole)
        return db_projectUserRole
    except IntegrityError as e:
        db.rollback()
        error_code = e.orig.args[0]  # Extract the error code
        #1062 is the error code for duplicate entry
        if error_code == 1062:
            raise HTTPException(status_code=400, detail="User already added to project")

def get_user_project(uid, project_id, db):
    return db.query(ProjectUserRole).filter(ProjectUserRole.uid == uid, ProjectUserRole.pid == project_id).first()


def remove_user_from_project(db, project_id, user_id):
    db_projectUserRole = db.query(ProjectUserRole).filter(ProjectUserRole.pid == project_id, ProjectUserRole.uid == user_id).first()
    db.delete(db_projectUserRole)
    db.commit()
    return db_projectUserRole


def update_user_role(db, project_id, user_id, role_id):
    db_projectUserRole = db.query(ProjectUserRole).filter(ProjectUserRole.pid == project_id, ProjectUserRole.uid == user_id).first()
    db_projectUserRole.rid = role_id
    db.commit()
    db.refresh(db_projectUserRole)
    return db_projectUserRole