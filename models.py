from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from database import Base
from datetime import datetime

class CommandHistory(Base):
    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_command = Column(String, index=True)
    parsed_json = Column(JSON)
    result_json = Column(JSON)
    is_chain_step = Column(Boolean, default=False)
