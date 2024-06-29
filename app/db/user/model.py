from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.role.model import Role

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True,index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(128))
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey('role.id'))

    role = relationship("Role",back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}), role={self.role.name}>"
