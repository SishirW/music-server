from typing import Optional, List
from pydantic import BaseModel, Field


class Genre(BaseModel):
    instrumentName: str
    count: int


class AddBandSchema(BaseModel):
    name: str = Field("Band Name")
    description: Optional[str] = Field("Description")
    genres: List[str] = list("str")
    skills: List[Genre]


class UpdateBandSchema(BaseModel):
    name: Optional[str] = Field("Band Name")
    location: Optional[str] = Field("")
    description: Optional[str] = Field("Description")
    genres: Optional[List[str]] = list("str")
