from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    task = relationship("Task",back_populates="status")
    projectStatus = relationship("ProjectStatus",back_populates="status")
    def __repr__(self):
        return f"Status('{self.name}', '{self.name}')"