from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.db.project import model, schema, crud
from app.db.database import SessionLocal, engine
from app.routers.authentication import get_current_user, oauth2_scheme

model.Base.metadata.create_all(bind=engine)

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
    # Create the project with the current user as the owner
    try:
        # Attempt to create the project with the current user as the owner
        return crud.create_project(db=db, project=schema.ProjectCreate(**project_data))
    except HTTPException as e:
        # If an HTTPException is raised, re-raise it to be handled by FastAPI
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        # For any other exceptions, you can return a generic error message
        # or log the exception for further investigation
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while creating the project.")

@router.get("/projects/", response_model=list[schema.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
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