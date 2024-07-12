from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.db.database import Base

class Task(Base):
    __tablename__ = "task"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    status_id = Column(Integer, ForeignKey('status.id'), nullable=False, index=True)
    description = Column(String(100))
    deadline = Column(DateTime, nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False, index=True)
    taskCategory_id = Column(Integer, ForeignKey('taskCategory.id'), nullable=False, index=True)

    project = relationship("Project", back_populates="task")
    taskCategory = relationship("TaskCategory", back_populates="task")
    status = relationship("Status", back_populates="task")

    def __repr__(self):
        return f"<Task Name: {self.name}> + <Task Description: {self.description}> + <Task Deadline: {self.deadline}> + <Task Project: {self.project}> + <Task Category: {self.taskCategory}> + <Task Status: {self.status}>"