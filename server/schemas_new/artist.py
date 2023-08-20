from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class CreateArtistSchema(BaseModel):
    alias: str
    description: str
    skills: List[str] =[]
    genre: List[str] =[]

class CreateScheduleSchema(BaseModel):
    venue: Optional[str]
    description: str= Field(...)
    start_time: datetime= Field()
    end_time: datetime= Field()

class EditScheduleSchema(BaseModel):
    venue: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class FollowArtistSchema(BaseModel):
    artist: str= Field(...)