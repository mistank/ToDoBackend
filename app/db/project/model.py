from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class Project(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    owner = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    description = Column(String(100))
    creation_date = Column(String(50))
    deadline = Column(String(50))

    user = relationship("User",back_populates="project")
    task = relationship("Task",back_populates="project")
    def __repr__(self):
        return f"<Project(name={self.name}, owner={self.owner}), description={self.description}, creation_date={self.creation_date}, deadline={self.deadline}>"