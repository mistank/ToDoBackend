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
    db_projectUserRole = model.ProjectUserRole(uid=user_id, pid=project_id, rid=role_id)
    db.add(db_projectUserRole)
    db.commit()
    db.refresh(db_projectUserRole)
    return db_projectUserRole


def get_user_project(uid, project_id, db):
    return db.query(ProjectUserRole).filter(ProjectUserRole.uid == uid, ProjectUserRole.pid == project_id).first()