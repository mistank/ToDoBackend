from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    id: int
    name: str
class Role(RoleBase):
    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True

