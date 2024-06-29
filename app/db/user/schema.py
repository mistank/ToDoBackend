from pydantic import BaseModel, ConfigDict

from app.db.role.schema import Role


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
