from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from app.db.user import model, schema, crud
from app.db.database import SessionLocal, engine

model.Base.metadata.create_all(bind=engine)

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users/", response_model=schema.User)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/users-bulk/", response_model=list[schema.User])
def create_users(users: list[schema.UserCreate], db: Session = Depends(get_db)):
    #i dont want to return the whole list, just the success message
    for user in users:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        crud.create_user(db=db, user=user)
@router.get("/users/", response_model=list[schema.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=schema.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/users/{username}", response_model=schema.UserBase)
def update_user(username: str, user: schema.UserBase, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    print("User je ", db_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user=user, user_id=db_user.id)

@router.delete("/users/{user_id}", response_model=schema.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)

@router.get("/users-from-project/{project_id}")
def get_users_for_project(project_id: int, db: Session = Depends(get_db)):
    users = crud.get_users_from_project(db, project_id)
    return users

@router.get("/search-users-not-from-project/{project_id}/{search}", response_model=list[schema.User])
def search_users_not_from_project(project_id: int, search: str, db: Session = Depends(get_db)):
    users = crud.search_users_not_from_project(db, project_id, search)
    return users

@router.get("/users-not-from-project/{project_id}/", response_model=list[schema.User])
def get_users_not_from_project(project_id: int, db: Session = Depends(get_db)):
    users = crud.get_users_not_from_project(db, project_id)
    return users
