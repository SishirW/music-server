from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from .venue import CreateSocialMedia
class CreateArtistSchema(BaseModel):
    alias: str
    description: str
    skills: List[str] =[]
    genre: List[str] =[]
    location: str
    looking_for: List[str]=[]
    #images: List[str]= Field(...)
    video: Optional[HttpUrl]
    social_media: CreateSocialMedia

class EditArtistSchema(BaseModel):
    alias: Optional[str]
    description: Optional[str]
    skills: Optional[List[str]]
    genre: Optional[List[str]]
    location: Optional[str]
    looking_for: Optional[List[str]]
    #images: List[str]= Field(...)
    video: Optional[HttpUrl]

    #social_media: CreateSocialMedia

class EditSocialMedia(BaseModel):
    facebook: Optional[HttpUrl]
    instagram: Optional[HttpUrl]
    youtube: Optional[HttpUrl]
    tiktok: Optional[HttpUrl]

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