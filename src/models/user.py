from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    todoist_token = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<User id={self.id}, telegram_id={self.telegram_id}>"
