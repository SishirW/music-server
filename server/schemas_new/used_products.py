from typing import Optional, List
from pydantic import BaseModel, EmailStr,Field
class CreateUsedProductSchema(BaseModel):
    name: str= Field(...)
    price: float= Field(...)
    description: str= Field(...)
    category: List[str]= Field(...)

class RequestToBuy(BaseModel):
    product_id: str= Field(...)
    name: str = Field(...)
    phone_no: int = Field(...)
    location: str = Field(...)