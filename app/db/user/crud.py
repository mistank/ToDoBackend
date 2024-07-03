from sqlalchemy.orm import Session

from app.db.user import model, schema
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(model.User).filter(model.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(model.User).filter(model.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = model.User(username=user.username, email=user.email, hashed_password=hashed_password,
                         permission_id=user.permission.id, firstName=user.firstName, lastName=user.lastName)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: schema.UserBase, user_id: int):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()
    db_user.username = user.username
    db_user.email = user.email
    db_user.firstName = user.firstName
    db_user.lastName = user.lastName
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db, user_id):
    db_user = db.query(model.User).filter(model.User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return db_user