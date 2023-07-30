from bson import ObjectId
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, root_validator
from datetime import datetime
import uuid


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class BaseModel(PydanticBaseModel):
    id: PyObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        validate_assignment = True

    @root_validator
    def number_validator(cls, values):
        values["updated_at"] = datetime.now()
        return values


class Image(BaseModel):
    user: PyObjectId= Field(...)
    image: str= Field(...)
    type: str= Field(...)

class Video(BaseModel):
    user: PyObjectId= Field(...)
    url: str

class Review(BaseModel):
    reviewer: PyObjectId= Field(...)
    reviewee: PyObjectId= Field(...)
    type: str
    rating: float
    comment: str