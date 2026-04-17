from sqlalchemy import Column, Integer, String, Text, Float
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    description = Column(Text)
    benefits = Column(Text)
    price = Column(Float)
