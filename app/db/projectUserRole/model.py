from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProjectUserRole(Base):
    __tablename__ = "projectUserRole"

    uid = Column(Integer,ForeignKey("user.id"), primary_key=True, )
    pid = Column(Integer,ForeignKey("project.id"),primary_key=True)
    rid = Column(Integer,ForeignKey("role.id"),primary_key=True)

    user = relationship("User",back_populates="projectUserRole")
    project = relationship("Project",back_populates="projectUserRole")
    role = relationship("Role",back_populates="projectUserRole")

