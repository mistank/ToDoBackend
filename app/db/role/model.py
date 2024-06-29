from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer,primary_key=True)
    name = Column(String(50),unique=True,index=True)

    user = relationship("User",back_populates="role")

