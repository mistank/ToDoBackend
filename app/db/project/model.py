from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    owner = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    description = Column(String(100))
    creation_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)

    user = relationship("User",back_populates="project")
    task = relationship("Task",back_populates="project",cascade="all, delete-orphan")
    projectStatus = relationship("ProjectStatus",back_populates="project", cascade="all, delete-orphan")
    projectUserRole = relationship("ProjectUserRole",back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(name={self.name}, owner={self.owner}), description={self.description}, creation_date={self.creation_date}, deadline={self.deadline}>"