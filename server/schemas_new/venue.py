from typing import Optional, List
from pydantic import BaseModel, EmailStr,Field
from datetime import datetime

class CreateVenueSchema(BaseModel):
    alias: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    category: List[str]= Field(...)

class CreatePackageSchema(BaseModel):
    name: str = Field(...)
    price: int = Field(...)
    date_time: datetime= Field(...)
    description: str = Field(...)

class CreateScheduleSchema(BaseModel):
    artist: Optional[str]
    description: str= Field(...)
    start_time: datetime= Field()
    end_time: datetime= Field()

class EditPackageSchema(BaseModel):
    name: Optional[str] 
    price: Optional[int] 
    date_time: Optional[datetime]
    description: Optional[str] 

class EditScheduleSchema(BaseModel):
    artist: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class BookPackageSchema(BaseModel):
    phone: int