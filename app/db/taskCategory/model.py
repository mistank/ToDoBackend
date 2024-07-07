from app.db.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class TaskCategory(Base):
    __tablename__ = "taskCategory"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    task = relationship("Task",back_populates="taskCategory")
    def __repr__(self):
        return f"<TaskCategory(name={self.name}, description={self.description})>"
