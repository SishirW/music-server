from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr,Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os
from server.schemas_new.venue import CreateReviewSchema,CreatePackageSchema, EditPackageSchema, BookPackageSchema, CreateScheduleSchema, EditScheduleSchema
from .venue_category import check_venuecategory_exists

collection_name= 'Venue'
package_collection_name= 'Package'
schedule_collection_name= 'VenueSchedule'
booking_collection_name= 'PackageBooking'
review_collection_name= 'VenueReview'
payment_collection_name= 'Transaction'
class Category(BaseModel):
    category: str

class VenueSchedule(BaseModel):
    venue: str= Field(...)
    artist: Optional[str]
    description: str
    start_time: datetime
    end_time: datetime

class VenueReview(BaseModel):
    reviewee: str
    reviewer: str
    venue: str
    rating: int
    review: str


class Payment(BaseModel):
    khalti_token: str
    idx: str
    phone: str
    amount: int
    amount_paid_in_rs: int
    package: str
    venue:str
    user_id:str
class Test(BaseModel):
    name: str

# class Payment(BaseModel):
#     khalti_token : str
#     idx: str
#     phone: str
#     amount: float
#     amount_in_rs: float
#     package: str
#     venue:str
#     user_id:str

class PackageBooking(BaseModel):
    package_id: str= Field(...)
    venue_id: str= Field(...)
    user_id: str= Field(...)
    complete: bool= False
    payment: str
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
    alias: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    category: List[str] = Field(...) 
    images: List[str]=[]
    is_featured: bool= False
    is_verified: bool= False
    user_id: str= Field(...)
    
async def add_venue(db, venue, user):
    category= [x for x in venue.category if await check_venuecategory_exists(x,db)]
    venue1= Venue(
       alias= venue.alias,
       location= venue.location,
       description= venue.description,
       category= category,
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
    pipeline= get_venue_detail_pipeline(id)  
    venue =await db[collection_name].aggregate(pipeline).to_list(1000)
    if venue==[]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venue not found!")
    return venue

async def check_venue_exists(db, id):
    artist = await db[collection_name].find_one({"_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Venue not found!")
    return artist

async def get_relevant_venue(db,page,category, search):
    if search != None:
        pipeline= get_search_pipeline(search, page)  
        venue =await db[collection_name].aggregate(pipeline).to_list(5)
    elif category != None:
        pipeline= get_category_pipeline(category, page)  
        venue =await db[collection_name].aggregate(pipeline).to_list(5)
    else:
      pipeline= get_pipeline(page)
      venue =await db[collection_name].aggregate(pipeline).to_list(5)
    return venue

async def get_featured_venue(db,page):
    venue =await db[collection_name].find({"is_featured":True}).skip((page-1)*5).limit(5).to_list(5)
    return venue

async def get_requested_venue(db,page):
    venue =await db[collection_name].find({"is_verified":False}).skip((page-1)*5).limit(5).to_list(5)
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


async def add_schedule(db,schedule: CreateScheduleSchema,user_id):
    venue= await get_venue_by_userid(db, user_id)
    sch= VenueSchedule(
        venue= venue['_id'],
        artist= schedule.artist,
        description= schedule.description, 
        start_time= schedule.start_time, 
        end_time= schedule.start_time,
    )
    encoded = jsonable_encoder(sch)
    await db[schedule_collection_name].insert_one(encoded)
    return {'success': True}


async def edit_schedule(db,schedule_id,schedule: EditScheduleSchema, user):
    schedule = {k: v for k, v in schedule.dict().items() if v is not None}
    check= await check_schedule_belongs_to_venue(db, schedule_id, user)
    if not check:
        raise HTTPException(status_code=404, detail=f"schedule not found")
    if len(schedule) >= 1:

        update_result = await db[schedule_collection_name].update_one(
            {"_id": schedule_id}, {"$set": schedule}
        )

        if update_result.modified_count == 1:
            if (
                updated_schedule := await db[schedule_collection_name].find_one({"_id": schedule_id})
            ) is not None:
                return updated_schedule

    if (
        existing_schedule := await db[schedule_collection_name].find_one({"_id": schedule_id})
    ) is not None:
        return existing_schedule

    raise HTTPException(status_code=404, detail=f"schedule with id {schedule_id} not found")

async def check_schedule_belongs_to_venue(db,schedule_id, user_id):
    schedule= await db[schedule_collection_name].find_one({"_id": schedule_id})
    if schedule is None:
        raise HTTPException(status_code=404, detail=f"schedule not found")
    venue=await get_venue_by_userid(db,user_id)
    return schedule['venue']== venue['_id']

async def delete_schedule(db, schedule_id, user):
    check= await check_schedule_belongs_to_venue(db, schedule_id, user)
    if not check:
        raise HTTPException(status_code=404, detail=f"schedule not found")
    schedule=await db[schedule_collection_name].delete_one({'_id': schedule_id})
    if schedule.deleted_count == 1:
        return {f"Successfully deleted schedule"}
    else:
        raise HTTPException(status_code=404, detail=f"schedule not found")


async def get_payment_by_id(db,id):
    payment= await db[payment_collection_name].find_one({"_id": id})
    if payment is None:
        raise HTTPException(status_code=404, detail=f"payment not found")
    return payment

async def get_venue_package_booking(db, package_id, user,page):
    venue= await get_venue_by_userid(db, user)
    print(venue)
    pipeline= get_venue_package_pipeline(package_id, venue['_id'], page)  
    reviews =await db[booking_collection_name].aggregate(pipeline).to_list(5)
    return reviews

async def book_package(db,user,booking: BookPackageSchema):
    package= await db[package_collection_name].find_one({"_id": booking.package})
    if package is None:
        raise HTTPException(status_code=404, detail=f"Package not found")
    payment_details= await complete_payment(db, package['venue_id'], booking.package,booking.payment, user)
    booking= PackageBooking(
        package_id= booking.package,
        venue_id= package['venue_id'],
        user_id= user,
        complete= True,
        payment= payment_details['_id'],
        booking_time= datetime.now(),
    )
    book= await db[booking_collection_name].insert_one(jsonable_encoder(booking))
    return {'success': True}
async def complete_payment(db ,venue,package,payment, user):
    payment= Payment(
        khalti_token=payment.khalti_token,
        idx=payment.idx,
        phone=payment.phone,
        amount=payment.amount,
        amount_paid_in_rs=payment.amount/100,
        package=package,
        venue= venue,
        user_id=user
    )
    await db[payment_collection_name].insert_one(jsonable_encoder(payment))
    payment_detail=await get_payment_by_id(db, str(payment.id))
    return payment_detail

async def add_review(db, review: CreateReviewSchema, user):
    venue= await check_venue_exists(db, review.venue)
    review= VenueReview(
        reviewee= venue["user_id"],
        reviewer= user,
        venue= review.venue,
        rating= review.rating,
        review= review.review
    )
    encoded = jsonable_encoder(review)
    await db[review_collection_name].insert_one(encoded)
    return {'success': True}

async def get_venue_review(db, id,page):
    venue= await check_venue_exists(db, id)
    pipeline= get_venue_review_pipeline(id, page)  
    reviews =await db[review_collection_name].aggregate(pipeline).to_list(5)
    return reviews


async def feature_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_featured': True}})
    print(result)
    return {"success":True}

async def unfeature_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_featured': False}})
    print(result)
    return {"success":True}

async def verify_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_verified': True}})
    print(result)
    return {"success":True}

async def unverify_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_verified': False}})
    print(result)
    return {"success":True}

def get_pipeline(page):
    return [
        {
            "$match": {
                "is_verified": True
            }
        },
  
  
  
  {
      "$sort":{
          "is_featured":-1,
          "_id":1,
      }
  },
  {
    "$skip": (page-1)*5
  },
  {
    "$limit": 5
  }
]

def get_search_pipeline(keyword, page):
    
    
    return [
      {
  "$match": {
    "alias": {
      "$regex": f".*{keyword}.*",
      "$options": "i"
    },
    "is_verified": True,
  }
  },
  
  
  
  {
    "$sort":{
        "is_featured":-1,
        "_id":1,
    }
  },
  {
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
]
  
  

def get_category_pipeline(category, page):
    return [
      {
            "$match": {
                "category": {
                    "$in": [category]
                },
                "is_verified": True
            }
        },
        
  
  {
    "$sort":{
        "is_featured":-1,
        "_id":1,
    }
  },
  {
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
]
    

def get_venue_detail_pipeline(id):
    return [
      {
            "$match": {
                "_id": id
            }
        },
        {
    "$lookup": {
      "from": "Package",
      "localField": "_id",
      "foreignField": "venue_id",
      "as": "package_details"
    }
  },
  {
    "$lookup": {
      "from": "VenueSchedule",
      "localField": "_id",
      "foreignField": "venue",
      "as": "schedule_details"
    }
  },
]

def get_venue_review_pipeline(id, page):
    return [
      {
            "$match": {
                "venue": id
            }
        },
        {
    "$lookup": {
      "from": "Users",
      "localField": "reviewer",
      "foreignField": "_id",
      "as": "user_details"
    }
        },
        {
            "$unwind": "$user_details"
        },
        {
            "$project": {
                "_id": 1,
                "reviewee": 1,
                "reviewer": 1,
                "venue": 1,
                "rating": 1,
                "review": 1,
                "username": "$user_details.username"
            }
        },
        
  {
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
]

def get_venue_package_pipeline(package, venue, page):
    return [
      {
            "$match": {
                "package_id": package,
                "venue_id": venue,
            }
        },
        {
    "$lookup": {
      "from": "Users",
      "localField": "user_id",
      "foreignField": "_id",
      "as": "user_details"
    },
    
        },
        {
    "$lookup": {
      "from": "Transaction",
      "localField": "payment",
      "foreignField": "_id",
      "as": "payment_details"
    },
    
        },
        
        {
            "$unwind": "$user_details"
        },
        {
            "$project": {
                "_id": 1,
                "package_id": 1,
                "venue_id": 1,
                "complete": 1,
                "payment": 1,
                "booking_time": 1,
                "username": "$user_details.username",
                "payment_details": "$payment_details",
            }
        },
         {
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
  
]