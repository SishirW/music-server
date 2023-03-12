from bson import ObjectId
from pydantic import Field
from . import BaseModel


class Instrument(BaseModel):
    name: str = Field(str)
    display_name: str = Field(str)
    iamge: str = Field(str)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "guitar",
                "display_name": "Guitar",
                "image": "",
            }
        }
