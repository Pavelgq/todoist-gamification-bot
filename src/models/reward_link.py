from sqlalchemy import Column, Integer, BigInteger, Float, ForeignKey, DateTime
from datetime import datetime
from src.models.base import Base
from sqlalchemy.orm import relationship


class RewardLink(Base):
    __tablename__ = 'reward_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    reward_id = Column(Integer, ForeignKey('rewards.id'), nullable=False)
    tag_id = Column(BigInteger, nullable=False)
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    reward = relationship("Reward", back_populates="reward_links")

    def __repr__(self):
        return (
            f"<RewardLink id={self.id}, user_id={self.user_id}, "
            f"reward_id={self.reward_id}, tag_id={self.tag_id}, value={self.value}>"
        )
