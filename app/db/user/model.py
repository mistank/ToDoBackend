from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.permission.model import Permission

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    username = Column(String(50), unique=True,index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(128))
    is_active = Column(Boolean, default=True)
    permission_id = Column(Integer, ForeignKey('permission.id'))

    reset_token = relationship("ResetToken",back_populates="user")
    project = relationship("Project",back_populates="user")
    permission = relationship("Permission",back_populates="user")
    projectUserRole = relationship("ProjectUserRole",back_populates="user")
    userTask = relationship("UserTask",back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}), permission={self.permission.name}>"
