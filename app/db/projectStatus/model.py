from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProjectStatus(Base):
    __tablename__ = 'projectStatus'

    sid = Column(Integer,ForeignKey('status.id'), primary_key=True)
    pid = Column(Integer,ForeignKey('project.id'), primary_key=True)

    project = relationship("Project",back_populates="projectStatus")
    status = relationship("Status",back_populates="projectStatus")
    def __repr__(self):
        return f"Status('{self.project}', '{self.status}')"