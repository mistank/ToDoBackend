from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.db.project import model, schema, crud
from app.db.projectUserRole import crud as projectUserRole_crud
from app.db.projectUserRole import schema as projectUserRole_schema
from app.db.projectUserRole import model as projectUserRole_model
from app.db.database import SessionLocal, engine
from app.routers.authentication import get_current_user, oauth2_scheme
from app.db.user import crud as user_crud
from app.db.role import model as role_model

model.Base.metadata.create_all(bind=engine)
role_model.Base.metadata.create_all(bind=engine)

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/projects/", response_model=schema.Project)
async def create_project(project: schema.ProjectBase, db: Session = Depends(get_db),
                         token: str = Depends(oauth2_scheme)):
    # Extract the current user from the token
    current_user = await get_current_user(token, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Modify the project data to include the current user as the owner
    project_data = project.dict()
    project_data['owner'] = current_user.id
    try:
        # Attempt to create the project with the current user as the owner
        return crud.create_project(db=db, project=schema.ProjectCreate(**project_data))
    except HTTPException as e:
        # If an HTTPException is raised, re-raise it to be handled by FastAPI
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/projects/add_user/", response_model=projectUserRole_schema.ProjectUserRole)
def add_user_to_project(project_id: int, user_id: int, role_id:int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return projectUserRole_crud.add_user_to_project(db=db, project_id=project_id, user_id=user_id, role_id=role_id)


@router.get("/projects/", response_model=list[schema.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects


#Projekti su na pocetku bili vracani samo za onog korisnika koji je vlasnik projekta,
#ali je dodata mogucnost da se vracaju svi projekti na kojima korisnik radi

#get all projects where uid is the logged in user in table projectUserRole
@router.get("/projects/working/", response_model=list[schema.Project])
async def read_working_projects(db: Session = Depends(get_db),
                                token: str = Depends(oauth2_scheme)):
    # Extract the current user from the token
    current_user = await get_current_user(token, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Get the projects on which the current user is working
    projects = crud.get_working_projects(db, user_id=current_user.id)
    print(projects)
    return [schema.Project.from_orm(project) for project in projects]


@router.get("/projects/owned/", response_model=list[schema.Project])
async def read_owned_projects(db: Session = Depends(get_db),
                                token: str = Depends(oauth2_scheme)):
    # Extract the current user from the token
    current_user = await get_current_user(token, db)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    # Get the projects owned by the current user
    projects = crud.get_owned_projects(db, owner_id=current_user.id)
    return projects

@router.get("/projects/{project_id}", response_model=schema.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/projects/{project_id}", response_model=schema.ProjectBase)
def update_project(project_id: int, project: schema.ProjectBase, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.update_project(db=db, project=project, project_id=db_project.id)

@router.delete("/projects/{project_id}", response_model=schema.ProjectBase)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.delete_project(db=db, project_id=db_project.id)