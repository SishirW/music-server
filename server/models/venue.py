from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr,Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os
from server.schemas_new.venue import CreatePackageSchema, EditPackageSchema, BookPackageSchema

collection_name= 'Venue'
package_collection_name= 'Package'
booking_collection_name= 'PackageBooking'

class Category(BaseModel):
    category: str

class VenueSchedule(BaseModel):
    title: str = Field(...)
    start_time: str = Field(...)
    end_time: Optional[str] = ''
    venue: str= Field(...)   # User.id
    artist: str= Field(...)  # User.id


class PaymentDetails(BaseModel):
    token: str
    idx: str
    phone: str
    amount_paid: int
    amount_paid_in_rs: int


class PackageBooking(BaseModel):
    package_id: str= Field(...)
    user_id: str= Field(...)
    phone: int
    complete: bool= False
    payment_details: Optional[PaymentDetails]
    booking_time: datetime


class Package(BaseModel):
    venue_id: str= Field(...)
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
    venue =await db[collection_name].find().skip((page-1)*5).limit(5).to_list(5)
    return venue

async def get_featured_venue(db,page):
    venue =await db[collection_name].find().sort(
            [('featured', -1)]).skip((page-1)*5).limit(5).to_list(5)
    return venue

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

async def add_package(db,package: CreatePackageSchema,user_id):
    venue= await get_venue_by_userid(db, user_id)
    print(venue)
    pkg= Package(
        venue_id= venue['_id'],
        name= package.name,
        price= package.price,
        date_time= package.date_time,
        description= package.description,
    )
    encoded = jsonable_encoder(pkg)
    await db[package_collection_name].insert_one(encoded)
    return {'success': True}


async def edit_package(db,package_id,package: EditPackageSchema, user):
    package = {k: v for k, v in package.dict().items() if v is not None}
    check= await check_package_belongs_to_venue(db, package_id, user)
    if not check:
        raise HTTPException(status_code=404, detail=f"Package not found")
    if len(package) >= 1:

        update_result = await db[package_collection_name].update_one(
            {"_id": package_id}, {"$set": package}
        )

        if update_result.modified_count == 1:
            if (
                updated_package := await db[package_collection_name].find_one({"_id": package_id})
            ) is not None:
                return updated_package

    if (
        existing_package := await db[package_collection_name].find_one({"_id": package_id})
    ) is not None:
        return existing_package

    raise HTTPException(status_code=404, detail=f"Package with id {package_id} not found")

async def check_package_belongs_to_venue(db,package_id, user_id):
    package= await db[package_collection_name].find_one({"_id": package_id})
    if package is None:
        raise HTTPException(status_code=404, detail=f"Package not found")
    venue=await get_venue_by_userid(db,user_id)
    return package['venue_id']== venue['_id']

async def delete_package(db, package_id, user):
    check= await check_package_belongs_to_venue(db, package_id, user)
    if not check:
        raise HTTPException(status_code=404, detail=f"Package not found")
    package=await db[package_collection_name].delete_one({'_id': package_id})
    if package.deleted_count == 1:
        return {f"Successfully deleted package"}
    else:
        raise HTTPException(status_code=404, detail=f"Package not found")

async def book_package(db,package_id,user,booking: BookPackageSchema):
    package= await db[package_collection_name].find_one({"_id": package_id})
    if package is None:
        raise HTTPException(status_code=404, detail=f"Package not found")
    book= PackageBooking(
        package_id= package_id,
        user_id= user,
        phone= booking.phone,
        booking_time= datetime.now()
    )
    encoded = jsonable_encoder(book)
    await db[booking_collection_name].insert_one(encoded)
    return {'success': True}




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

def delete_schedule():
    pass

def complete_booked_package():
    pass


