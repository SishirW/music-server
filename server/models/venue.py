from . import BaseModel, PydanticBaseModel, PyObjectId, Image, Review, Video
from typing import List, Optional, EmailStr, Field
from .bands import Location
from datetime import datetime

class Category(BaseModel):
    category: str

class VenueSchedule(BaseModel):
    title: str = Field(...)
    start_time: str = Field(...)
    end_time: Optional[str] = ''
    venue: PyObjectId= Field(...)   # User.id
    artist: PyObjectId= Field(...)  # User.id


class PaymentDetails(BaseModel):
    token: str
    idx: str
    phone: str
    amount_paid: int
    amount_paid_in_rs: int


class PackageBooking(BaseModel):
    package_id: PyObjectId= Field(...)
    user_id: PyObjectId= Field(...)
    venue_id: PyObjectId= Field(...)
    # name: str
    # email: str
    phone: str
    complete: bool
    payment_details: PaymentDetails
    booking_time: datetime


class Package(BaseModel):
    venue_id: PyObjectId= Field(...)
    name: str = Field(...)
    price: int = Field(...)
    time: datetime.time
    date: datetime.date
    valid: Optional[bool] = True
    description: str = Field(...)
    points: int = 0



class Venue(BaseModel):
    name: str = Field(...)   # separate name or user name ???
    #location: str = Field(...)
    description: str = Field(...)
    #menu: Optional[List] = []  # How to define in Image class ??? 
    #video: Optional[str] = ''
    category: PyObjectId = Field(...) 
    is_featured: bool
    is_verified: bool
    owner_id: PyObjectId= Field(...)
    
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


