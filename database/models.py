from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String(255), nullable=False)  # Увеличили длину
    phone = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
