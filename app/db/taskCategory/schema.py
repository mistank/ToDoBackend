from typing import Optional

from pydantic import BaseModel

class TaskCategoryBase(BaseModel):
    name: str



class TaskCategory(TaskCategoryBase):
    id: int

    class Config:
        from_orm = True
        from_attributes = True  # orm mode
        arbitrary_types_allowed = True