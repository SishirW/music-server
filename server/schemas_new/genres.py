from typing import Optional
from pydantic import BaseModel, Field


class AddGenreSchema(BaseModel):
    name: str = Field("rnr")
    display_name: str = Field('Rock and Role')
    image: Optional[str] = Field('base64 icon')


class UpdateGenreSchema(BaseModel):
    name: Optional[str] = Field("hiphop")
    display_name: Optional[str] = Field('Hip-Hop')
    image: Optional[str] = Field('base64 image')
