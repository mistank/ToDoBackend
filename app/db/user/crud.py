from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.db.user import model, schema
from passlib.context import CryptContext
from app.db.project import model as project_model
from app.db.projectUserRole import model as projectUserRole_model
from app.exceptions import handle_database_error, handle_not_found


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    try:
        return db.query(model.User).filter(model.User.id == user_id).first()
    except Exception as e:
        handle_database_error(e, "Get user")


def get_user_by_email(db: Session, email: str):
    try:
        return db.query(model.User).filter(model.User.email == email).first()
    except Exception as e:
        handle_database_error(e, "Get user by email")


def get_user_by_username(db: Session, username: str):
    try:
        return db.query(model.User).filter(model.User.username == username).first()
    except Exception as e:
        handle_database_error(e, "Get user by username")


def get_users(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(model.User).offset(skip).limit(limit).all()
    except Exception as e:
        handle_database_error(e, "Get users")


def create_user(db: Session, user: schema.UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = model.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            permission_id=2,
            firstName=user.firstName,
            lastName=user.lastName
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "username" in error_msg.lower():
            handle_database_error(e, "Create user", detail="Username already registered")
        elif "email" in error_msg.lower():
            handle_database_error(e, "Create user", detail="Email already registered")
        else:
            handle_database_error(e, "Create user")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create user")


def update_user(db: Session, user: schema.UserBase, user_id: int):
    try:
        db_user = db.query(model.User).filter(model.User.id == user_id).first()
        if not db_user:
            handle_not_found("User", user_id)

        db_user.username = user.username
        db_user.email = user.email
        db_user.firstName = user.firstName
        db_user.lastName = user.lastName
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e)
        if "username" in error_msg.lower():
            handle_database_error(e, "Update user", detail="Username already exists")
        elif "email" in error_msg.lower():
            handle_database_error(e, "Update user", detail="Email already exists")
        else:
            handle_database_error(e, "Update user")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Update user")


def delete_user(db, user_id):
    try:
        db_user = db.query(model.User).filter(model.User.id == user_id).first()
        if not db_user:
            handle_not_found("User", user_id)

        db.delete(db_user)
        db.commit()
        return db_user
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Delete user")


def get_users_from_project(db, project_id):
    try:
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
    except Exception as e:
        handle_database_error(e, "Get users from project")


def get_users_not_from_project(db, project_id):
    try:
        #project-user-role -> pur
        purs = db.query(projectUserRole_model.ProjectUserRole).options(
            joinedload(projectUserRole_model.ProjectUserRole.user),
        ).filter(projectUserRole_model.ProjectUserRole.pid == project_id).all()
        users_on_project = [pur.user for pur in purs]
        all_users = db.query(model.User).all()
        #return the difference between all users and users on project
        return [user for user in all_users if user not in [user_on_project for user_on_project in users_on_project]]
    except Exception as e:
        handle_database_error(e, "Get users not from project")


def create_users(db, users):
    try:
        created_users = []
        for user in users:
            hashed_password = pwd_context.hash(user.password)
            db_user = model.User(
                username=user.username,
                email=user.email,
                hashed_password=hashed_password,
                permission_id=2,
                firstName=user.firstName,
                lastName=user.lastName
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            created_users.append(db_user)
        return created_users
    except IntegrityError as e:
        db.rollback()
        handle_database_error(e, "Create users", detail="One or more users already exist")
    except Exception as e:
        db.rollback()
        handle_database_error(e, "Create users")


def search_users_not_from_project(db, project_id, search):
    try:
        result = [
            user for user in get_users_not_from_project(db, project_id)
            if search.lower() in user.firstName.lower() or search.lower() in user.lastName.lower()
        ]
        return result
    except Exception as e:
        handle_database_error(e, "Search users not from project")