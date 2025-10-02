from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import engine
from app.routers.authentication import get_db
from app.db.role import model, schema

model.Base.metadata.create_all(bind=engine)

router = APIRouter()

@router.get("/roles/")
def read_roles(db: Session = Depends(get_db)):
    roles = db.query(model.Role).all()
    print(roles)
    return roles

@router.get("/roles/{role_id}")
def read_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(model.Role).filter(model.Role.id == role_id).first()
    return role

@router.post("/roles/")
def create_role(role: schema.Role, db: Session = Depends(get_db)):
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@router.put("/roles/{role_id}")
def update_role(role_id: int, role: schema.Role, db: Session = Depends(get_db)):
    db_role = db.query(model.Role).filter(model.Role.id == role_id).first()
    db_role.name = role.name
    db.commit()
    db.refresh(db_role)
    return db_role

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    db_role = db.query(model.Role).filter(model.Role.id == role_id).first()
    db.delete(db_role)
    db.commit()
    return db_role

