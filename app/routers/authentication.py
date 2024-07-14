import secrets
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated, Union

from aiosmtplib import smtp
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from google.auth.transport import requests
from google.oauth2 import id_token
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.csrf import generate_csrf_token
from app.db.resetToken import model as resetToken_model
from app.db.resetToken import crud as resetToken_crud
from app.db.permission.schema import Permission
from app.db.user import model as user_model
from app.db.permission import model as role_model
from app.db.user.schema import User, UserCreate, UserBase
from app.db.user import crud as user_crud
from app.db.database import SessionLocal, engine
import jwt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic_settings import BaseSettings
import smtplib
from pydantic import EmailStr


class Settings(BaseSettings):
    MAIL_USERNAME: str = "milan"
    MAIL_PASSWORD: str = "Sarenileptir"
    MAIL_FROM: str = "milan.stankovic02@outlook.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.outlook.com"
    MAIL_FROM_NAME: str = "To Do App"
    MAIL_STARTTLS: bool = True  # Assuming STARTTLS should be enabled
    MAIL_SSL_TLS: bool = False  # Assuming SSL/TLS is not required

    class Config:
        env_file = ".env"

settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,  # Added
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,    # Added
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)


router = APIRouter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

user_model.Base.metadata.create_all(bind=engine)
role_model.Base.metadata.create_all(bind=engine)
resetToken_model.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    user: User


# class User(BaseModel):
#     username: str
#     email: Union[str, None] = None
#     disabled: Union[bool, None] = None

# class UserInDB(User):
#     hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def email_formatter(email: str):
    email_before_monkey = str.split(email, "@")[0]
    email_after_monkey = str.split(email, "@")[1]
    email_before_monkey = email_before_monkey.replace(".", "")
    email = email_before_monkey + "@" + email_after_monkey
    return email
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    return db.query(user_model.User).filter(user_model.User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def verify_google_token(token: str):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), "1077121873039-4v7vq2v5j0e1f0g1q7k3kq0v3q3q1q8.apps.googleusercontent.com")
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        return idinfo['email']
    except ValueError:
        return None
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.get('/current-user', response_model=User)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("Username is None")
            raise credentials_exception
        user = get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user
    except InvalidTokenError:
        raise credentials_exception



async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User.from_orm(user)
    )


@router.post("/signup", response_model=Token)
async def signup(
        user_data: UserCreate,
        db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_username(db, user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = get_password_hash(user_data.password)
    email = email_formatter(user_data.email)
    new_user = user_model.User(username=email, hashed_password=hashed_password, email=user_data.email, permission_id=2, firstName=user_data.firstName, lastName=user_data.lastName, is_active=1)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", user=User.from_orm(new_user))

@router.post("/google-login/{email}", response_model=Token)
async def google_login(email: str,
        db: Session = Depends(get_db)
):

    print("Email: ",email)
    #remove the dots before the @ character in the email
    email = email_formatter(email)
    user = user_crud.get_user_by_email(db, email)
    print("User: ", user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not registered",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User.from_orm(user)
    )

@router.post("/google-signup", response_model=Token)
async def google_signup(
        userInfo: UserBase,
        db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_email(db, userInfo.email)
    print("User: ", user)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )
    hashed_password = get_password_hash("google")
    email = email_formatter(userInfo.email)
    new_user = user_model.User(username=userInfo.firstName + " " +  userInfo.lastName, hashed_password=hashed_password, email=email, permission_id=2, firstName=userInfo.firstName, lastName=userInfo.lastName, is_active=1)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", user=User.from_orm(new_user))

async def send_reset_email(email_to: str, token: str):
    port = 587  # or 465 for SSL
    smtp_server = "smtp-mail.outlook.com"
    login = "milan.stankovic02@outlook.com"
    password = "Sarenileptir"
    sender_email = "milan.stankovic02@outlook.com"
    receiver_email = email_to

    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset your password"
    message["From"] = sender_email
    message["To"] = receiver_email

    html = f"""\
    <html>
    <body>
        <p>Hi,<br>
        Reset your password by clicking the link below.<br>
        <a href="http://localhost:5173/reset-password?token={token}">Reset Password</a>
        </p>
    </body>
    </html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    # Connect to the server
    server = smtplib.SMTP(smtp_server, port)
    server.set_debuglevel(1)  # Optional: gives detailed output

    # Secure the connection
    server.starttls()  # Upgrade the connection to SSL/TLS
    server.login(login, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()

@router.post("/forgot-password/{email}")
async def forgot_password(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    reset_token = secrets.token_urlsafe()
    # Store the reset token with an expiration time
    await resetToken_crud.store_reset_token(db, user.id, reset_token)
    background_tasks.add_task(send_reset_email, email_to=email, token=reset_token)
    return {"message": "If an account with this email was found, a password reset link has been sent."}

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., example="q_hXNKr1P0IjO-sxxavbmLrYWOU8ToLCWieUA5hY5Qo")
    new_password: str = Field(..., example="sarenileptir")
@router.post("/reset-password/")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = resetToken_crud.verify_reset_token(db, request.token)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    user.hashed_password = pwd_context.hash(request.new_password)
    db.commit()
    return {"message": "Password has been reset successfully."}

