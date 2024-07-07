from pydantic import BaseModel


class StatusBase(BaseModel):
    name: str


class Status(StatusBase):
    id: int

    class Config:
        from_orm = True
        orm_mode = True
        from_attributes = True
