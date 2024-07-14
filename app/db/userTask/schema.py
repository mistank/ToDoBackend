from pydantic import BaseModel


class UserTaskBase(BaseModel):
    uid: int
    tid: int

class UserTaskCreate(UserTaskBase):
    pass

class UserTask(UserTaskBase):

        class Config:
            orm_mode = True
            arbitrary_types_allowed = True