import datetime
from fastapi import HTTPException
from app.db.project import model
from sqlalchemy.exc import IntegrityError
def get_project(db, project_id: int):
    return db.query(model.Project).filter(model.Project.id == project_id).first()


def get_projects(db, skip: int = 0, limit: int = 100):
    return db.query(model.Project).offset(skip).limit(limit).all()



def create_project(db, project):
    try:
        db_project = model.Project(name=project.name, owner=project.owner, description=project.description,
                                   creation_date=datetime.date.today().strftime('%d-%m-%Y'), deadline=project.deadline)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except IntegrityError as e:
        db.rollback()
        error_code = e.orig.args[0]  # Extract the error code
        print(type(error_code))
        #1062 is the error code for duplicate entry
        if error_code == 1062:
            raise HTTPException(status_code=400, detail="Project name already exists")



def update_project(db, project, project_id: int):
    db_project = db.query(model.Project).filter(model.Project.id == project_id).first()
    db_project.name = project.name
    db_project.owner = project.owner
    db_project.description = project.description
    db_project.creation_date = project.creation_date
    db_project.deadline = project.deadline
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db, project_id: int):
    db_project = db.query(model.Project).filter(model.Project.id == project_id).first()
    db.delete(db_project)
    db.commit()
    return db_project
