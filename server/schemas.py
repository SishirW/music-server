from pydoc import describe
from pydantic import BaseModel
from typing import List

class Images(BaseModel):
    name: str
    url: str

    class Config:
        orm_mode = True

class CreateProduct(BaseModel):
    name: str
    price: float
    seller: str
    description: str

    class Config:
        orm_mode = True
class Product(CreateProduct):
    
    images: List[Images]= []
    
    class Config:
        orm_mode = True