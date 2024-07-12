import secrets
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated, Union

from aiosmtplib import smtp
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.csrf import generate_csrf_token
from app.db.resetToken import model as resetToken_model
from app.db.resetToken import crud
from app.db.permission.schema import Permission
from app.db.user import model as user_model
from app.db.permission import model as role_model
from app.db.database import SessionLocal, engine
import jwt
from app.db.user.schema import User, UserCreate
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


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.get('/current-user',response_model=User)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print("Token: ",token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload: ", payload)
        username: str = payload.get("sub")
        print("Username: ", username)
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


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
    user = get_user(db, user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    hashed_password = get_password_hash(user_data.password)
    new_user = user_model.User(username=user_data.username, hashed_password=hashed_password, email=user_data.email, permission_id=2, firstName=user_data.firstName, lastName=user_data.lastName, is_active=1)
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
    await crud.store_reset_token(db, user.id, reset_token)
    background_tasks.add_task(send_reset_email, email_to=email, token=reset_token)
    return {"message": "If an account with this email was found, a password reset link has been sent."}

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., example="q_hXNKr1P0IjO-sxxavbmLrYWOU8ToLCWieUA5hY5Qo")
    new_password: str = Field(..., example="sarenileptir")
@router.post("/reset-password/")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = crud.verify_reset_token(db, request.token)
    if not user:
        raise HTTPException(status_code=404, detail="Invalid or expired token")
    user.hashed_password = pwd_context.hash(request.new_password)
    db.commit()
    return {"message": "Password has been reset successfully."}

# Assuming you have a UserToken model with user_id, token, and expires fields
# async def store_reset_token(db: Session, user_id: int, token: str):
#     expire_at = datetime.now() + timedelta(hours=1)  # Token expires in 1 hour
#     db_token = resetToken_model.ResetToken(user_id=user_id, token=token, expires=expire_at)
#     db.add(db_token)
#     db.commit()
#
# def verify_reset_token(db: Session, token: str):
#     db_token = db.query(resetToken_model.ResetToken).filter(resetToken_model.ResetToken.token == token, resetToken_model.ResetToken.expires > datetime.now()).first()
#     if db_token:
#         return db.query(user_model.User).filter(user_model.User.id == db_token.user_id).first()
#     return None