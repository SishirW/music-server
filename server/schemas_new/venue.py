from typing import Optional, List
from pydantic import BaseModel, EmailStr,Field

class CreateVenueSchema(BaseModel):
    alias: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    category: str= Field(...)