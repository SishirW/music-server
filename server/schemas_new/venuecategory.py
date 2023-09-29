from typing import Optional
from pydantic import BaseModel, Field


class AddVenueCategorySchema(BaseModel):
    name: str = Field("restaurant")
    display_name: str = Field('Restaurant')
    image: Optional[str] = Field('base64 icon')


class UpdateVenueCategorySchema(BaseModel):
    name: Optional[str] = Field("restaurant")
    display_name: Optional[str] = Field('Restaurant')
    image: Optional[str] = Field('base64 image')
