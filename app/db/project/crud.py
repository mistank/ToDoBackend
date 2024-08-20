from datetime import datetime
from fastapi import HTTPException
from app.db.project import model, schema
from sqlalchemy.exc import IntegrityError
from app.db.projectUserRole import model as projectUserRole_model
def get_project(db, project_id: int):
    return db.query(model.Project).filter(model.Project.id == project_id).first()


def get_projects(db, skip: int = 0, limit: int = 100):
    return db.query(model.Project).offset(skip).limit(limit).all()

def get_owned_projects(db, owner_id: int):
    return db.query(model.Project).filter(model.Project.owner == owner_id).all()


def create_project(db, project):
    try:
        db_project = model.Project(name=project.name, owner=project.owner, description=project.description,
                                   creation_date=datetime.now(), deadline=project.deadline)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        db_projectUserRole = projectUserRole_model.ProjectUserRole(uid=project.owner, pid=db_project.id, rid=1)
        db.add(db_projectUserRole)
        db.commit()
        db.refresh(db_projectUserRole)
        return db_project
    except IntegrityError as e:
        db.rollback()
        error_code = e.orig.args[0]  # Extract the error code
        print(type(error_code))
        #1062 is the error code for duplicate entry
        if error_code == 1062:
            raise HTTPException(status_code=400, detail="Project name already exists")



def update_project(db, project:schema.Project, project_id: int):
    db_project = db.query(model.Project).filter(model.Project.id == project_id).first()
    db_project.name = project.name
    db_project.description = project.description
    db_project.deadline = project.deadline
    db.commit()
    db.refresh(db_project)
    print(db_project)
    return db_project


def delete_project(db, project_id: int):
    db_project = db.query(model.Project).filter(model.Project.id == project_id).first()
    db.delete(db_project)
    db.commit()
    return db_project


def get_working_projects(db, user_id):
# get all projects where uid is the logged in user in table projectUserRole
    return db.query(model.Project).filter(model.Project.id == projectUserRole_model.ProjectUserRole.pid).filter(projectUserRole_model.ProjectUserRole.uid == user_id).all()


def get_related_projects(db, user_id):
    #izvlacenje svih projekata koji su vezani sa korisnikom u tabeli projectUserRole
    return db.query(model.Project).filter(model.Project.id == projectUserRole_model.ProjectUserRole.pid).filter(projectUserRole_model.ProjectUserRole.uid == user_id).all()


    # owned_projects = get_owned_projects(db, user_id)
    # working_projects = get_working_projects(db, user_id)
    # projects = owned_projects + working_projects
    # return projects
