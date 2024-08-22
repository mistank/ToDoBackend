from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class Role(RoleBase):

    class Config:
        from_attributes = True  # orm mode
        arbitrary_types_allowed = True