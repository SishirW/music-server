from .database import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

class Products(Base):
    __tablename__ = "products"
    id= Column(Integer, primary_key= True, index= True)
    name= Column(String)
    price= Column(Float)
    seller= Column(String)
    description= Column(String)
    images = relationship("Images", back_populates="parent")

class Images(Base):
    __tablename__ = "product_images"
    id= Column(Integer, primary_key= True, index= True)
    name= Column(String)
    url= Column(String)
    parent_id = Column(Integer, ForeignKey("products.id"))
    parent= relationship("Products", back_populates="images")



