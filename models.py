from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    available = Column(String)
    price = Column(Integer)
    image = Column(String)
    url = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=func.now())

