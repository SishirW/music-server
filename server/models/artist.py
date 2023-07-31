from . import BaseModel, PydanticBaseModel, PyObjectId, Image, Review
from typing import List, Optional, EmailStr, Field
from .bands import Location
from datetime import datetime

class Skill(BaseModel):
    skill: str

class Genre(BaseModel):
    genre: str

class ArtistSchedule(BaseModel):
    artist: PyObjectId= Field(...)
    venue: PyObjectId= Field(...)
    start_time: datetime
    end_time: datetime

class ArtistFollow(BaseModel):
    artist: PyObjectId= Field(...)
    user: PyObjectId= Field(...)

class Artist(BaseModel):
    name: str
    #location: str = Field(...)
    description: str
    skills: List[PyObjectId]
    genre: List[PyObjectId]
    is_featured: bool
    #video: Optional[str]
    user_id: PyObjectId= Field(...)

