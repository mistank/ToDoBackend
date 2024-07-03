from app.db.database import Base

class Role(Base):
    id: int
    name: str

    class Config:
        from_attributes = True  # orm mode
        arbitrary_types_allowed = True

