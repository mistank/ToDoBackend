from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), nullable=False)
    description = Column(String(100))
    deadline = Column(String(50))
    project = Column(Integer, ForeignKey('project.id'), nullable=False, index=True)
    taskCategory = Column(Integer, ForeignKey('taskCategory.id'), nullable=False, index=True)

    project_rel = relationship("Project",back_populates="task")
    taskCategory_rel = relationship("TaskCategory",back_populates="task")