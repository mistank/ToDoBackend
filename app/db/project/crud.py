from datetime import datetime
from fastapi import HTTPException
from app.db.project import model, schema
from sqlalchemy.exc import IntegrityError
from app.db.projectUserRole import model as projectUserRole_model
from app.db.user import model as user_model
from app.db.project import model as project_model
from sqlalchemy.orm import joinedload
from fastapi import status
from app.exceptions import handle_database_error, handle_not_found

def get_project(db, project_id: int):
    try:
        return db.query(model.Project).filter(model.Project.id == project_id).first()
    except Exception as e:
        handle_database_error(e, "Get project")


def get_projects(db, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.Project).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get projects")

def get_owned_projects(db, owner_id: int):
    try:
        return db.query(model.Project).filter(model.Project.owner == owner_id).all()
    except Exception as e:
        handle_database_error(e, "Get owned projects")


def create_project(db, project):
    try:
        db_project = model.Project(
            name=project.name,
            owner=project.owner,
            description=project.description,
            creation_date=datetime.now(),
            deadline=project.deadline
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

        db_projectUserRole = projectUserRole_model.ProjectUserRole(
            uid=project.owner,
            pid=db_project.id,
            rid=1
        )
        db.add(db_projectUserRole)
        db.commit()
        db.refresh(db_projectUserRole)

        return db_project

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Create project", detail="Project name already exists")
        else:
            handle_database_error(e, "Create project")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create project")



def update_project(db, project:schema.Project, project_id: int):
    try:
        db_project = db.query(model.Project).filter(model.Project.id == project_id).first()
        if not db_project:
            handle_not_found("Project", project_id)

        db_project.name = project.name
        db_project.description = project.description
        db_project.deadline = project.deadline
        db.commit()
        db.refresh(db_project)
        print(db_project)
        return db_project
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "name" in error_msg.lower():
            handle_database_error(e, "Update project", detail="Project name already exists")
        else:
            handle_database_error(e, "Update project")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update project")


def delete_project(db, project_id: int):
    try:
        db_project = db.query(model.Project).filter(model.Project.id == project_id).first()
        if not db_project:
            handle_not_found("Project", project_id)

        db.delete(db_project)
        db.commit()
        return db_project
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete project")


def get_working_projects(db, user_id):
# get all projects where uid is the logged in user in table projectUserRole
    try:
        return db.query(model.Project).filter(model.Project.id == projectUserRole_model.ProjectUserRole.pid).filter(projectUserRole_model.ProjectUserRole.uid == user_id).all()
    except Exception as e:
        handle_database_error(e, "Get working projects")


def get_related_projects(db, user_id):
    #izvlacenje svih projekata koji su vezani sa korisnikom u tabeli projectUserRole
    try:
        return db.query(model.Project) \
            .join(projectUserRole_model.ProjectUserRole, model.Project.id == projectUserRole_model.ProjectUserRole.pid) \
            .filter(projectUserRole_model.ProjectUserRole.uid == user_id) \
            .options(joinedload(model.Project.user)) \
            .all()
    except Exception as e:
        handle_database_error(e, "Get related projects")

    # owned_projects = get_owned_projects(db, user_id)
    # working_projects = get_working_projects(db, user_id)
    # projects = owned_projects + working_projects
    # return projects
