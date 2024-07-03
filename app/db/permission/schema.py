from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    id: int
    name: str
class Permission(PermissionBase):
    class Config:
        from_attributes = True # orm mode
        arbitrary_types_allowed = True

