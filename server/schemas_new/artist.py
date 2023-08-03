from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class CreateArtistSchema(BaseModel):
    alias: str
    description: str
    skills: List[str] =[]
    genre: List[str] =[]