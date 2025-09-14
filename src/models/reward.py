from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base

class Reward(Base):
    __tablename__ = 'rewards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    unit = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    reward_links = relationship("RewardLink", back_populates="reward")
    
    def __repr__(self):
        return f"<Reward id={self.id}, name={self.name!r}, unit={self.unit!r}>"

    def __str__(self):
        return f"{self.name} ({self.unit})"
