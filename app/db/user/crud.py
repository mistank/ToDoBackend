from sqlalchemy.orm import Session, joinedload

from app.db.user import model, schema
from passlib.context import CryptContext
from app.db.project import model as project_model
from app.db.projectUserRole import model as projectUserRole_model


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


def get_users_from_project(db, project_id):
    user_roles = db.query(projectUserRole_model.ProjectUserRole).options(
        joinedload(projectUserRole_model.ProjectUserRole.user),
        joinedload(projectUserRole_model.ProjectUserRole.role)
    ).filter(projectUserRole_model.ProjectUserRole.pid == project_id).all()

    result = [
        {
            'id': user_role.user.id,
            'firstName': user_role.user.firstName,
            'lastName': user_role.user.lastName,
            'username': user_role.user.username,
            'email': user_role.user.email,
            'role_name': user_role.role.name
        }
        for user_role in user_roles
    ]

    return result


def get_users_not_from_project(db, project_id):
    #project-user-role -> pur
    purs = db.query(projectUserRole_model.ProjectUserRole).options(
        joinedload(projectUserRole_model.ProjectUserRole.user),
    ).filter(projectUserRole_model.ProjectUserRole.pid == project_id).all()
    users_on_project = [pur.user for pur in purs]
    all_users = db.query(model.User).all()
    #return the difference between all users and users on project
    return [user for user in all_users if user not in [user_on_project for user_on_project in users_on_project]]


def create_users(db, users):
    for user in users:
        hashed_password = pwd_context.hash(user.password)
        db_user = model.User(username=user.username, email=user.email, hashed_password=hashed_password,
                             permission_id=2, firstName=user.firstName, lastName=user.lastName)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return users


def search_users_not_from_project(db, project_id, search):
    result = [
        user for user in get_users_not_from_project(db, project_id)
        if search.lower() in user.firstName.lower() or search.lower() in user.lastName.lower()
    ]

    return result