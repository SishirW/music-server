from typing import Optional, List
from pydantic import BaseModel, EmailStr,Field
from datetime import datetime

class CreateVenueSchema(BaseModel):
    alias: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    category: str= Field(...)

class CreatePackageSchema(BaseModel):
    name: str = Field(...)
    price: int = Field(...)
    date_time: datetime= Field(...)
    description: str = Field(...)

class EditPackageSchema(BaseModel):
    name: Optional[str] 
    price: Optional[int] 
    date_time: Optional[datetime]
    description: Optional[str] 


class BookPackageSchema(BaseModel):
    phone: int