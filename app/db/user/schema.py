from pydantic import BaseModel, ConfigDict

from app.db.permission.schema import Permission


class UserBase(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str


class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True
