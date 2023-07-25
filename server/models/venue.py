from . import BaseModel, PydanticBaseModel
from typing import List, Optional, EmailStr, Field
from .bands import Location
from datetime import datetime

class Category(BaseModel):
    category: str

class Schedule(BaseModel):
    id: str = Field(alias='_id')
    title: str = Field(...)
    start_time: str = Field(...)
    end_time: Optional[str] = ''

class VenueSocialMedia(BaseModel):
    facebook: Optional[str]
    instagram: Optional[str]
    tiktok: Optional[str]
    youtube: Optional[str]
    twitter: Optional[str]

class Rating(BaseModel):
    venue_id: str
    user_id: str
    rating: float
    comment: str

class PaymentDetails(BaseModel):
    token: str
    idx: str
    phone: str
    amount_paid: int
    amount_paid_in_rs: int

class PackageBooking(BaseModel):
    package_id: str
    user_id: str
    # name: str
    # email: str
    phone: str
    complete: bool
    payment_details: PaymentDetails
    booking_time: datetime


class Package(BaseModel):
    venue_id: str
    name: str = Field(...)
    price: int = Field(...)
    time: str = Field(...)
    date: str = Field(...)
    valid: Optional[bool] = True
    bookings: Optional[List] = []
    description: str = Field(...)
    points: int = 0

class Venue(BaseModel):
    name: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    images: Optional[List] = []
    todays_schedule: Optional[List[Schedule]] = []
    menu: Optional[List] = [] 
    video: Optional[str] = ''
    social: VenueSocialMedia
    category: str 
    #avg_rating: int
    #no_of_rating: int
    owner_id: str
    
def create_venue():
    pass

def get_venue_by_id():
    pass

def get_venues():
    pass

def get_requested_venues():
    pass

def edit_venue():
    pass

def get_venue():   # Venue owned by logged in user
    pass

def get_venue_packages():
    pass

def get_venue_booking_details():
    pass

def get_venue_rating():
    pass

def delete_venue():
    pass

def delete_featured_venue():
    pass

def update_package():
    pass

def update_schedule():
    pass

def validate_venue():
    pass

def invalidate_package():
    pass

def delete_package():
    pass

def delete_schedule():
    pass

def book_package():
    pass

def complete_booked_package():
    pass


