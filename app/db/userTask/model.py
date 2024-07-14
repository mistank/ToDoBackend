from app.db.database import Base
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class UserTask(Base):
    __tablename__ = "userTask"

    uid = Column(Integer, ForeignKey('user.id'),primary_key=True)
    tid = Column(Integer, ForeignKey('task.id'),primary_key=True)

    user = relationship("User",back_populates="userTask")
    task = relationship("Task",back_populates="userTask")


