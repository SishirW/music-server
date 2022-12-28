from optparse import Option
from pydoc import describe
from unicodedata import category
import uuid
from bson import ObjectId, _get_float
from pydantic import BaseModel, Field
from typing import List, Optional,  Union
import datetime

# Product schemas

class ProductRating(BaseModel):
    product_id: str
    rating: float
    comment: str

class ProductQuestion(BaseModel):
    product_id: str
    comment: str
    answer: Optional[bool]= False
class ViewProductQuestions(BaseModel):
    comment: str
    answer: Optional[bool]= False

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

class OrderNumber(BaseModel):
    id: str
    quantity: int

class OrderProduct(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    product_ids: List[OrderNumber]
    status: str= 'processing'
    user_id: str
    type: str
    date_time: datetime.datetime = datetime.datetime.now()

class GetProductRating(BaseModel):
    rating: str
    comment: str
    user_image: str
    user_name: str

class CreateProductCategory(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    category: str= Field(...)

class ShowProductCategory(BaseModel):
    category: str

# User schemas
class ShowUserType(BaseModel):
    type: str

class ShowUser(ShowUserType):
    full_name: str
    username: str
    email: str
class ShowUserDetails(ShowUser):
    orders: List 
class EditUserAdditionalDetails(BaseModel):
    location: Optional[str]
    phone_no: Optional[str]

class GetAdditionalDetails(EditUserAdditionalDetails):
    full_name: str
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
    type: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: ShowUserWithId


class TokenData(BaseModel):
    username: Union[str, None] = None

class CreateUser(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    full_name: str= Field(...)
    username: str= Field(...)
    email: str= Field(...)
    password: str= Field(...)
    verified: bool= True
    type: str= "user"
    cart: List=[]
    location: Optional[str]=''
    phone_no: Optional[str]=''
    orders: Optional[List]=[]
    following: Optional[List]=[]


# Venues Schemas


class VenueSocialMedia(BaseModel):
    facebook: Optional[str]
    instagram: Optional[str]
    tiktok: Optional[str]
    youtube: Optional[str]
    twitter: Optional[str]

class VenueRating(BaseModel):
    venue_id: str
    rating: float
    comment: str

class GetVenueRating(BaseModel):
    rating: str
    comment: str
    user_image: str
    user_name: str

class Package(BaseModel):
    id: str= Field(alias='_id')
    package: str=Field(...)
    price: float=Field(...)
    time: str=Field(...)
    valid: Optional[bool]=True
    bookings: Optional[List]=[]


class ShowVenue(BaseModel):
    id: str= Field(alias='_id')
    name: str
    location: str
    description: str
    images: List
    todays_schedule: List
    menu: str
    video: str
    social: VenueSocialMedia
    packages: List[Package]

class ShowVenueAdmin(BaseModel):
    id: str= Field(alias='_id')
    name: str
    location: str
    description: str
    images: List
    todays_schedule: List
    menu: str
    video: str
    social: VenueSocialMedia
    packages: List
class EditVenue(BaseModel):
    name: Optional[str]
    location: Optional[str]
    description: Optional[str]
    todays_schedule: Optional[List]
    menu: Optional[str]
    video: Optional[str]
    social: Optional[str]
    packages: Optional[List]

class Schedule(BaseModel):
    id: str= Field(alias='_id')
    title: str= Field(...)
    start_time: str=Field(...)
    end_time: Optional[str]=''


class CreateVenue(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    name: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    images: Optional[List]=[]
    todays_schedule: Optional[List[Schedule]]=[]
    menu: Optional[str]=''
    video: Optional[str]=''
    social: VenueSocialMedia
    packages:Optional[List[Package]]=[]

class CreateVenueCategory(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    category: str= Field(...)

class ShowVenueCategory(BaseModel):
    category: str

#Artist 

class Followers(BaseModel):
    id: str= Field(...)
    type: str=Field(...)
class CreateArtist(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    name: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    images: Optional[List]=[]
    followers: Optional[List[Followers]]=[]
    following: Optional[List]=[]
    skills: List
    looking_for: Optional[List]=[]
class ShowArtist(BaseModel):
    id :Optional[str]= Field(default_factory=uuid.uuid4, alias='_id')
    name: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    images: Optional[List]=[]
    skills: List
    looking_for: Optional[List]=[]
    follows: bool
    
class Followers(BaseModel):
    id: str= Field(...)
    type: str=Field(...)

    


