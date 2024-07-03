from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class ProjectUserRole(Base):
    __tablename__ = "projectUserRole"

    uid = Column(Integer,primary_key=True)
    pid = Column(Integer,primary_key=True)
    rid = Column(Integer,primary_key=True)

    user = relationship("User",back_populates="projectUserRole")
    project = relationship("Project",back_populates="projectUserRole")
    role = relationship("Role",back_populates="projectUserRole")

