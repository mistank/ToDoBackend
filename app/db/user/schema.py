from pydantic import BaseModel, ConfigDict

from app.db.permission.schema import Permission
from app.db.role.schema import Role


class UserBase(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str


class UserCreate(UserBase):
    password: str

class UserRole(UserBase):
    role: Role

class User(UserBase):
    id: int

    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
