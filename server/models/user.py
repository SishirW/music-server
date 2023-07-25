from . import BaseModel, PydanticBaseModel
from typing import List, Optional, EmailStr, Field
from .bands import Location
from datetime import datetime

class ValidationToken(PydanticBaseModel):
    number: int
    created_at: datetime



class User(BaseModel):
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    verified: bool = True
    type: Optional[str] = "user"
    #cart: List = []     # QN
    location: Optional[Location] = ''
    phone_no: Optional[str] = ''
    devices: List[str]
    points: int
    validation_token: List[ValidationToken]
    #orders: Optional[List] = []   # QN (Require Order class ?)
    #following: Optional[List] = [] # QN

    # bookings: ????

# class Cart(BaseModel):
#     user_id: str
#     product_id: str
#     quantity: str


class UserFollowing(BaseModel):
    user_id: str
    artist_id: str

def create_user():
    pass

def verify_user():
    pass

def get_user_by_id():
    pass

def get_user_by_username():
    pass

def get_user_by_email():
    pass

# def check_is_artist():
#     pass
# def check_is_venue():
#     pass

def validate_seller():
    pass

def validate_artist():
    pass

def validate_venue():
    pass

def validate_user():
    pass

def validate_admin():
    pass


def edit_user_details():
    pass

def get_users():  #Admin
    pass

def delete_user():
    pass


def get_bookings_detail():
    pass


def add_device():
    pass

def remove_device():
    pass
