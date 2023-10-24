from typing import Optional, List
from pydantic import BaseModel,Field, HttpUrl
from datetime import datetime


class CreateSocialMedia(BaseModel):
    facebook: Optional[HttpUrl]
    instagram: Optional[HttpUrl]
    youtube: Optional[HttpUrl]
    tiktok: Optional[HttpUrl]

class CreateVenueSchema(BaseModel):
    alias: str= Field(...)
    location: str= Field(...)
    description: str= Field(...)
    category: List[str]= Field(...)
    #menu: List[str]= Field(...)
    video: Optional[HttpUrl]= None
    social_media: CreateSocialMedia

class EditVenueSchema(BaseModel):
    alias: Optional[str]
    location: Optional[str]
    description: Optional[str]
    category: Optional[List[str]]
    video: Optional[HttpUrl]= None

class CreatePackageSchema(BaseModel):
    name: str = Field(...)
    price: int = Field(...)
    description: str = Field(...)
    seats_per_day: int
    start_time: datetime
    end_time: datetime
    booking_cost: float
    reward_points: int

class CreateScheduleSchema(BaseModel):
    artist: Optional[str]
    description: str= Field(...)
    start_time: datetime
    end_time: datetime

class CreateReviewSchema(BaseModel):
    venue: str
    rating: int
    review: str

class EditPackageSchema(BaseModel):
    name: Optional[str] 
    price: Optional[int] 
    date_time: Optional[datetime]
    description: Optional[str] 
    valid: Optional[bool]

class EditScheduleSchema(BaseModel):
    artist: Optional[str]
    description: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class PaymentSchema(BaseModel):
    khalti_token : str
    idx: str
    phone: str
    amount: float
    package: str
    venue:str
    user_id:str


class AddBookingPaymentSchema(BaseModel):
    khalti_token: str
    idx: str
    phone: str
    amount: int

class BookPackageSchema(BaseModel):
    package: str
    phone: int
    payment: AddBookingPaymentSchema
    booking_time: datetime= datetime.now()
    seats: int

