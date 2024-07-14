from pydantic import BaseModel


class RoleBase(BaseModel):
    id: int
    name: str

class RoleCreate(RoleBase):
    name: str

class Role(RoleBase):

    class Config:
        from_attributes = True  # orm mode
        arbitrary_types_allowed = True