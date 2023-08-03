from . import BaseModel, PydanticBaseModel, PyObjectId, Image, Review, Video
from typing import List, Optional
from pydantic import EmailStr,Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os

collection_name= 'Venue'

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
    date_time: datetime
    valid: Optional[bool] = True
    description: str = Field(...)
    points: int = 0



class Venue(BaseModel):
    alias: str = Field(...)   # separate name or user name ???
    location: str = Field(...)
    description: str = Field(...)
    category: str = Field(...) 
    images: List[str]=[]
    is_featured: bool= False
    is_verified: bool= False
    user_id: str= Field(...)
    
async def add_venue(db, venue, user):
    venue1= Venue(
       alias= venue.alias,
       location= venue.location,
       description= venue.description,
       category= venue.category,
       user_id=user
   )
    encoded = jsonable_encoder(venue1)
    await db[collection_name].insert_one(encoded)
    return {'success': True}


async def get_venue_by_userid(db, id):
    venue = await db[collection_name].find_one({"user_id": id})
    if venue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"venue not found!")
    return venue

async def get_venue_byid(db, id):
    venue = await db[collection_name].find_one({"_id": id})
    if venue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"venue not found!")
    return venue

async def get_relevant_venue(db,page):
    venue = db[collection_name].find().skip((page-1)*5).limit(5)
    venues=[]
    async for a in venue:
        venues.append(a)
    return venues

async def get_featured_venue(db,page):
    venue = db[collection_name].find().sort(
            [('featured', -1)]).skip((page-1)*5).limit(5)
    venues=[]
    async for a in venue:
        venues.append(a)

    return venues

async def add_images(db,venue_id, files):
    names = []
    if files is not None:
        for file in files:
            image_name = uuid.uuid4()
            os.makedirs(f'media_new/venue/{venue_id}', exist_ok=True)
            with open(f"media_new/venue/{venue_id}/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            names.append(f"{image_name}.png")
        db[collection_name].update_one({'_id': venue_id}, {'$push': {'images': {'$each':names}}})
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')

def get_venues():
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


