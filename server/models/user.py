from . import BaseModel, PydanticBaseModel, PyObjectId
from typing import List, Optional
from pydantic import EmailStr, Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException,status
from ..password_methods import get_password_hash


collection_name = "Users"

class ValidationToken(BaseModel):
    number: int
    created_at: datetime

class UserType(BaseModel):
    typeName: str

class SocialMedia(BaseModel):
    facebook: Optional[str] =''
    instagram: Optional[str]=''
    tiktok: Optional[str]=''
    youtube: Optional[str]=''
    twitter: Optional[str]=''

class Token(BaseModel):
    user: str
    token: int
    created_at: datetime

class User(BaseModel):
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    verified: bool = True
    type: str= 'user'
    location: Optional[str] = ''
    phone_no: Optional[str] = ''
    devices: List[str]= []
    points: int =0
    social_links: Optional[SocialMedia]


async def create_user(db, user):
    old_user= await db[collection_name].find_one({"email": user.email})
    if old_user is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with email {user.email} already exists!")
    old_user= await db[collection_name].find_one({"username": user.username})
    if old_user is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with username {user.username} already exists!")
    
    user1 = User(
        full_name= user.full_name,
        username= user.username,
        email= user.email,
        password= get_password_hash(user.password),
    )
    encoded = jsonable_encoder(user1)
    print(encoded)
    await db[collection_name].insert_one(encoded)
    # new_user = await find_band_by_id(db, str(bnd.id), user)
    # return new_band
    return {'success': True}


async def find_user_by_id(db, id):
    user = await db[collection_name].find_one({"_id": id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    return user

async def find_user_by_email(db, email):
    user = await db[collection_name].find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    return user

async def find_user_by_username(db, username):
    user = await db[collection_name].find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    return user


async def delete_user_by_id(db, id):
    user = await db[collection_name].delete_one({'_id': id})
    if user.deleted_count != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found")

async def edit_user_details(db, id,user_info):
    user_info = {k: v for k, v in user_info.dict().items() if v is not None}

    if len(user_info) >= 1:

        update_result = await db[collection_name].update_one(
            {"_id": id}, {"$set": user_info}
        )

        if update_result.modified_count == 1:
            if (
                updated_user_info := await db[collection_name].find_one({"_id": id})
            ) is not None:
                return updated_user_info

    if (
        existing_user_info := await db[collection_name].find_one({"_id": id})
    ) is not None:
        return existing_user_info

    raise HTTPException(status_code=404, detail=f"User with id {id} not found")

def verify_user():
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


# def edit_user_details():
#     pass

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
