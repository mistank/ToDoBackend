from pydantic import BaseModel, ConfigDict

from app.db.role.schema import Role


class UserBase(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    role: Role


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
