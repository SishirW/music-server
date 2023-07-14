from typing import Optional
from pydantic import BaseModel, Field


class AddInstrumentSchema(BaseModel):
    name: str = Field("guitar")
    display_name: str = Field('Guitar')
    image: Optional[str] = Field('base64 image')


class UpdateInstrumentSchema(BaseModel):
    name: Optional[str] = Field("guitar")
    display_name: Optional[str] = Field('Guitar')
    image: Optional[str] = Field('base64 image')
