from optparse import Option
from pydoc import describe
from unicodedata import category
import uuid
from bson import ObjectId, _get_float
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional,  Union, Dict
import datetime
import pytz


tz = pytz.timezone('Asia/Kathmandu')

# Product schemas


class ProductRating(BaseModel):
    product_id: str
    rating: float
    comment: str


class ProductQuestion(BaseModel):
    product_id: str
    comment: str
    answer: Optional[bool] = False


class ViewProductQuestions(BaseModel):
    comment: str
    answer: Optional[bool] = False


class CreateProduct(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    price: float = Field(...)
    description: str = Field(...)
    category: str = Field(...)
    points: int = Field(...)
    # avg_rating: Optional[float]=0.0

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
        orm_mode = True


class ShowProduct(BaseModel):
    id: str = Field(alias='_id')
    name: str
    price: float
    description: str
    images: List
    category: str


class ShowProductCart(ShowProduct):
    quantity: int


class ShowProductAdmin(ShowProduct):
    id: str = Field(alias='_id')


class OptionalProduct(BaseModel):
    name: str


class EditProduct(BaseModel):
    name: Optional[str]
    price: Optional[float]
    description: Optional[str]
    points: Optional[str]
    # new_image: Optional[str]
    # images_to_delete:Optional[List[str]]


class OrderNumber(BaseModel):
    id: str
    quantity: int


class OrderProduct(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    product_ids: List[OrderNumber]
    status: str = 'processing'
    user_id: str
    type: str
    date_time: datetime.datetime = datetime.datetime.now()
    khalti_details: Optional[Dict]


class GetProductRating(BaseModel):
    rating: str
    comment: str
    user_image: str
    user_name: str


class CreateProductCategory(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    category: str = Field(...)


class ShowProductCategory(BaseModel):
    category: str

# User schemas


class ShowUserType(BaseModel):
    type: str


class ShowUser(ShowUserType):
    full_name: str
    username: str
    email: str


class ShowUserWithDetails(ShowUserType):
    full_name: str
    username: str
    email: str
    points: int
    orders: List
    following: List
    details: Dict


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
        orm_mode = True


class ShowUserWithId(ShowUser):
    id: str = Field(alias='_id')
    type: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: ShowUserWithId


class TokenData(BaseModel):
    username: Union[str, None] = None


class CreateUser(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    verified: bool = True
    type: Optional[str] = "user"
    cart: List = []
    location: Optional[str] = ''
    phone_no: Optional[str] = ''
    orders: Optional[List] = []
    following: Optional[List] = []
    # created_at: datetime.datetime = datetime.datetime.now()


class UserDetails(BaseModel):
    id: str = Field(alias='_id')
    full_name: str
    username: str
    email: str
    type: str
    verified: bool
    location: str
    phone_no: str


class ShowUserDetailsAdmin(BaseModel):
    has_next: bool
    users: List[UserDetails]
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
    id: str = Field(alias='_id')
    # venue_id: str= Field(...)
    name: str = Field(...)
    price: int = Field(...)
    time: str = Field(...)
    date: str = Field(...)
    valid: Optional[bool] = True
    bookings: Optional[List] = []
    description: str = Field(...)
    points: int = 0

# class PaymentInfo(BaseModel):
#     token: str= Field(...)
#     idx: str= Field(...)
#     phone: str= Field(...)
#     amount_paid: str= Field(...)
#     amount_paid_in_rs: str= Field(...)


class EditPackage(BaseModel):
    name: Optional[str]
    price: Optional[float]
    time: Optional[str]
    valid: Optional[bool]


class ShowVenue(BaseModel):
    id: str = Field(alias='_id')
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
    id: str = Field(alias='_id')
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
    images: Optional[List]
    menu: Optional[List]
    category: Optional[str]
    video: Optional[str]
    social: Optional[Dict]


class Schedule(BaseModel):
    id: str = Field(alias='_id')
    title: str = Field(...)
    start_time: str = Field(...)
    end_time: Optional[str] = ''


class CreateVenue(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    images: Optional[List] = []
    todays_schedule: Optional[List[Schedule]] = []
    menu: Optional[List] = []
    video: Optional[str] = ''
    social: VenueSocialMedia
    category: str = Field(...)
    # packages:Optional[List[Package]]=[]


class CreateFeatured(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    venue_id: str
    package_id: Optional[str]
    type: str = "venue"
    image: str


class CreateVenueCategory(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    category: str = Field(...)


class ShowVenueCategory(BaseModel):
    category: str

# Artist


class Followers(BaseModel):
    id: str = Field(...)
    type: str = Field(...)


class CreateArtist(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    category: str = Field(...)
    images: Optional[List] = []
    followers: Optional[List[Followers]] = []
    following: Optional[List] = []
    skills: str
    looking_for: Optional[str] = ''
    featured: Optional[bool] = False
    todays_schedule: Optional[List[Schedule]] = []
    video: Optional[str] = ''
    social: VenueSocialMedia


class ShowArtist(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    images: Optional[List] = []
    skills: List
    looking_for: Optional[List] = []
    follows: bool
    following_no: int
    followers_no: int
    featured: bool
    category: str


class ArtistSchedule(BaseModel):
    id: str = Field(alias='_id')
    venue: str = Field(...)
    start_time: str = Field(...)
    end_time: Optional[str] = ''


class ShowArtistEdited(BaseModel):
    id: str = Field(alias='_id')
    name: str
    location: str
    description: str
    images: Optional[List] = []
    skills: List
    looking_for: Optional[List] = []


class EditArtist(BaseModel):
    name: Optional[str]
    location: Optional[str]
    description: Optional[str]
    images: Optional[List]
    skills: Optional[List]
    looking_for: Optional[List]
    category: Optional[str]
    video: Optional[str]
    social: Optional[Dict]


class CreateArtistCategory(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    category: str = Field(...)


class ShowArtistCategory(BaseModel):
    category: str


class Followers(BaseModel):
    id: str = Field(...)
    type: str = Field(...)


# Grow

class GrowForm(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    type: str = Field(...)
    instrument: Optional[str] = ''
    category: str = Field(...)
    email: str = Field(...)
    phone: int = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    previous_course: str = Field(...)


class GrowVideoForm(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    video_url: str = Field(...)


# Used product
class CreateUsedProduct(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    price: int = Field(...)
    seller_name: str = Field(...)
    seller_phone: int = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    seller_id: Optional[str]
    category: str = Field(...)
    images: List[str] = Field(...)

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
        orm_mode = True


class ShowUsedProduct(BaseModel):
    id: str = Field(alias='_id')
    name: str
    price: float
    # seller: str
    description: str
    images: List
    category: str


class ShowUsedProductAdmin(BaseModel):
    id: str = Field(alias='_id')
    name: str
    price: int
    # seller: str
    description: str
    location: str
    images: List
    category: str
    seller_name: str
    seller_phone: int
    seller_email: str
    requests_to_buy: List


class GetUsedProduct(BaseModel):
    has_next: bool
    products: List[ShowUsedProduct]


class GetUsedProductAdmin(BaseModel):
    has_next: bool
    products: List[ShowUsedProductAdmin]


class EditUsedProduct(BaseModel):
    name: Optional[str]
    price: Optional[int]
    seller_name: Optional[str]
    seller_phone: Optional[int]
    location: Optional[str]
    description: Optional[str]
    category: Optional[str]
    images: Optional[List[str]]


class RequestToBuy(BaseModel):
    name: str = Field(...)
    phone_no: int = Field(...)
    location: str = Field(...)


# Repair

class RepairForm(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')

    instrument: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    email: str = Field(...)
    phone: int = Field(...)
    location: str = Field(...)
    date_time: Optional[datetime.datetime]
    images: List[str] = Field(...)


# Advertisment

class AddAdvertisment(BaseModel):
    id: Optional[str] = Field(default_factory=uuid.uuid4, alias='_id')
    name: str = Field(...)
    image: str = Field(...)
    url: str = Field(...)
    starting_image: Optional[str] = ''
