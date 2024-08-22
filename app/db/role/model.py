from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    projectUserRole = relationship("ProjectUserRole",back_populates="role")
    def __repr__(self):
        return f"Role('{self.name}', '{self.name}')"

