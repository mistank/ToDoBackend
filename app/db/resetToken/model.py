from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class ResetToken(Base):
    __tablename__ = "resetToken"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(100), index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    expires = Column(DateTime)

    user = relationship("User", back_populates="reset_token")
