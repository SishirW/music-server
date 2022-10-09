from optparse import Option
from pydoc import describe
from unicodedata import category
import uuid
from bson import ObjectId, _get_float
from pydantic import BaseModel, Field
from typing import List, Optional,  Union


# Product schemas

class ProductRating(BaseModel):
    product_id: str
    rating: float
    comment: str

class CreateProduct(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    name: str= Field(...)
    price: float= Field(...)
    seller: str= Field(...)
    description: str= Field(...)
    seller_id: Optional[str]
    category: str= Field(...)
    

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
        orm_mode=True

class ShowProduct(BaseModel):
    id: str= Field(alias='_id')
    name: str
    price: float
    seller: str
    description: str
    images: List
    category: str


class ShowProductCart(ShowProduct):
    quantity: int

class ShowProductAdmin(ShowProduct):
    id: str= Field(alias='_id')



class OptionalProduct(BaseModel):
    name: str

class EditProduct(BaseModel):
    name: Optional[str]
    price: Optional[float]
    seller: Optional[str]
    description: Optional[str]
    #new_image: Optional[str]
    #images_to_delete:Optional[List[str]]

class CreateProductCategory(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    category: str= Field(...)

class ShowProductCategory(BaseModel):
    category: str

# User schemas

class ShowUser(BaseModel):
    full_name: str
    username: str
    email: str

class ShowCart(BaseModel):
    cart: List

class AddToCart(BaseModel):
    product_id: str
    quantity: int
    class Config:
        orm_mode=True

class ShowUserWithId(ShowUser):
    id: str= Field(alias='_id')

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
    is_seller: bool= False
    is_venue: bool= False
    is_superuser: bool= False
    cart: List=[]



# Venues Schemas
class ShowVenue(BaseModel):
    name: str
    location: str
    description: str
    images: List

class CreateVenue(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    name: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    

