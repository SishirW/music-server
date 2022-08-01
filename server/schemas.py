from optparse import Option
from pydoc import describe
import uuid
from bson import ObjectId, _get_float
from pydantic import BaseModel, Field
from typing import List, Optional,  Union


class CreateProduct(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    name: str= Field(...)
    price: float= Field(...)
    seller: str= Field(...)
    description: str= Field(...)
    

    class Config:
        allow_population_by_field_name = True
        # schema_extra = {
        #     "example": {
        #         "id": "00010203-0405-0607-0809-0a0b0c0d0e0f",
        #         "name": "Piano",
        #         "price" :10000,
        #         "seller": "Shop",
        #         "description": "hdhsgh dgshgds ",
                
        #     }
        # }

class ShowProduct(BaseModel):
    name: str
    price: float
    seller: str
    description: str
    images: List


class EditProduct(BaseModel):
    name: Optional[str]
    price: Optional[float]
    seller: Optional[str]
    description: Optional[str]
    #new_image: Optional[str]
    images_to_delete:Optional[List[str]]



class ShowUser(BaseModel):
    full_name: str
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: ShowUser


class TokenData(BaseModel):
    username: Union[str, None] = None

class CreateUser(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    full_name: str
    username: str
    email: str
    password: str



