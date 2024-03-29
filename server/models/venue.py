from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr,Field,HttpUrl
from .bands import Location
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os
from server.schemas_new.artist import EditSocialMedia
from server.schemas_new.venue import  EditVenueSchema,CreateVenueSchema,CreateReviewSchema,CreatePackageSchema, EditPackageSchema, BookPackageSchema, CreateScheduleSchema, EditScheduleSchema
from .venue_category import check_venuecategory_exists
from .payment import complete_booking_payment
import requests
from .orders import khalti_url
from .payment import AddBookingPayment
from .user import collection_name as user_collection_name
collection_name= 'Venue'
package_collection_name= 'Package'
schedule_collection_name= 'VenueSchedule'
booking_collection_name= 'PackageBooking'
review_collection_name= 'VenueReview'
points_collection_name= 'RewardPoints'
social_media_collection_name= 'SocialMedia'
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




class PackageBooking(BaseModel):
    package_id: str= Field(...)
    venue_id: str= Field(...)
    user_id: str= Field(...)
    complete: bool= False
    payment: str
    booking_time: datetime
    seats: int
    phone_no:str



class Package(BaseModel):
    venue_id: str= Field(...)
    name: str = Field(...)
    price: int = Field(...)
    valid: Optional[bool] = True
    description: str = Field(...)
    seats_per_day: int
    start_time: datetime
    end_time: datetime
    booking_cost: float
    reward_points: int

class SocialMedia(BaseModel):
    facebook: Optional[HttpUrl]
    instagram: Optional[HttpUrl]
    youtube: Optional[HttpUrl]
    tiktok: Optional[HttpUrl]

class Venue(BaseModel):
    alias: str = Field(...)
    location: str = Field(...)
    description: str = Field(...)
    category: List[str] = Field(...) 
    images: List[str]=[]
    is_featured: bool= False
    is_verified: bool= True
    menu: List[str]=[]
    video: HttpUrl= None
    user_id: str= Field(...)
    social_accounts: str
    
async def add_venue(db, venue: CreateVenueSchema, user):
    category= [x for x in venue.category if await check_venuecategory_exists(x,db)]
    social= SocialMedia(
        facebook= venue.social_media.facebook,
        instagram= venue.social_media.instagram,
        youtube= venue.social_media.youtube,
        tiktok= venue.social_media.tiktok,
    )
    social_encoded= jsonable_encoder(social)
    social_media_detail= await db[social_media_collection_name].insert_one(social_encoded)
    social_media_id= social_media_detail.inserted_id
    venue1= Venue(
       alias= venue.alias,
       location= venue.location,
       description= venue.description,
       category= category,
       user_id=user,
       social_accounts= social_media_id,
       video= venue.video,
   )
    encoded = jsonable_encoder(venue1)
    insert_venue=await db[collection_name].insert_one(encoded)
    detail= await db[collection_name].find_one({'_id': insert_venue.inserted_id})
    return detail


async def edit_venue(db,artist: EditVenueSchema, user):
    artist = {k: v for k, v in artist.dict().items() if v is not None}
    artist_check= await db[collection_name].find_one({'user_id': user})
    if artist_check is None:
        raise HTTPException(status_code=404, detail=f"artist not found")
    artist_id= artist_check['_id']
    if len(artist) >= 1:

        update_result = await db[collection_name].update_one(
            {"_id": artist_id}, {"$set": artist}
        )

        if update_result.modified_count == 1:
            if (
                updated_artist := await db[collection_name].find_one({"_id": artist_id})
            ) is not None:
                return updated_artist

    if (
        existing_artist := await db[collection_name].find_one({"_id": artist_id})
    ) is not None:
        return existing_artist

    raise HTTPException(status_code=404, detail=f"Venue with id {artist_id} not found")

async def get_venue_by_userid(db, id):
    print(id)
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
      venue =await db[collection_name].aggregate(pipeline).to_list(12)
    return venue


async def get_featured_venue(db,page):
    pipeline= get_featured_pipeline(page)
    venue =await db[collection_name].aggregate(pipeline).to_list(12)
    return venue

async def get_requested_venue(db,page):
    venue =await db[collection_name].find({"is_verified":False}).skip((page-1)*5).limit(5).to_list(5)
    return venue


async def add_images(db,venue_id, files, type=0):
    names = []
    if files is not None:
        for file in files:
            image_name = uuid.uuid4()
            os.makedirs(f'media_new/venue/{venue_id}', exist_ok=True)
            with open(f"media_new/venue/{venue_id}/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            names.append(f"{image_name}.png")
        if type==0:
            db[collection_name].update_one({'_id': venue_id}, {'$push': {'images': {'$each':names}}})
        else:
            db[collection_name].update_one({'_id': venue_id}, {'$push': {'menu': {'$each':names}}})
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')

async def add_package(db,package: CreatePackageSchema,user_id):
    venue= await get_venue_by_userid(db, user_id)
    pkg= Package(
        venue_id= venue['_id'],
        name= package.name,
        price= package.price,
        description= package.description,
        seats_per_day= package.seats_per_day,
        start_time= package.start_time,
        end_time= package.end_time,
        booking_cost= package.booking_cost,
        reward_points= package.booking_cost,
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

async def delete_venue(db, id):
    check= await check_venue_exists(db, id)

    if not check:
        raise HTTPException(status_code=404, detail=f"Venue not found")
    venue= await db[collection_name].find_one({'_id': id})
    deleted_venue=await db[collection_name].delete_one({'_id': id})
    await db[user_collection_name].update_one({"_id": venue['user_id']}, {"$set": {'type': 'user'}})
    if deleted_venue.deleted_count == 1:
        return {f"Successfully deleted package"}
    else:
        raise HTTPException(status_code=404, detail=f"Package not found")

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
        end_time= schedule.end_time,
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

async def delete_images(db, id, files, type):
    empty=[]
    for image in files:
        if type==0:
            update_result= await db[collection_name].update_one({'_id': id}, {'$pull': {'images': image}})
        else:
            update_result= await db[collection_name].update_one({'_id': id}, {'$pull': {'menu': image}})
        if update_result.modified_count == 0:
            empty.append(image)
    if len(empty) == 0:
        return {"detail": "Successfully deleted image", "not_found": []}
    else:
        return {"detail": "Some images were missing", "not_found": empty}


async def get_venue_package_booking(db, package_id, user,page):
    venue= await get_venue_by_userid(db, user)
    print(venue)
    pipeline= get_venue_package_pipeline(package_id, venue['_id'], page)  
    reviews =await db[booking_collection_name].aggregate(pipeline).to_list(5)
    return reviews

async def check_seat_available(db, package_id, booking_date, seats):
    package= await db[package_collection_name].find_one({"_id": package_id})
    if package is None or package['valid']== False:
        raise HTTPException(status_code=404, detail=f"Package not found")
    start_date = datetime.fromisoformat(str(package['start_time'])).replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat(str(package['end_time'])).replace(tzinfo=timezone.utc)
    date_to_check = datetime.fromisoformat(str(booking_date)).replace(tzinfo=timezone.utc)
    if not start_date <= date_to_check <= end_date:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot book on this date")
    booked_seats= await check_seats_on_date(db, date_to_check.date(), package_id)
    print(booked_seats)
    if (package['seats_per_day']- booked_seats)< seats:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Cannot book this number of seats")
    return {'available': True}
    
async def book_package(db,user,booking: BookPackageSchema):
    package= await db[package_collection_name].find_one({"_id": booking.package})
    if package is None or package['valid']== False:
        raise HTTPException(status_code=404, detail=f"Package not found")
    
    payload = {
        'token': booking.payment.khalti_token,
        'amount': booking.payment.amount
        }
    headers = {
        'Authorization': 'Key test_secret_key_a290c9bfc87a4c3f9016af3055f3e882'
    }
    
    response = requests.request("POST", khalti_url, headers=headers, data=payload)
    if response.status_code== 200:
        payment_details= await complete_booking_payment(db, package['venue_id'], booking.package,booking.payment, user) 
    else:
        raise HTTPException(status_code=response.status_code, detail= response.text)
    booking= PackageBooking(
        package_id= booking.package,
        venue_id= package['venue_id'],
        user_id= user,
        complete= False,
        payment= payment_details['_id'],
        booking_time= booking.booking_time,
        seats= booking.seats,
        phone_no= booking.phone,

    )
    book= await db[booking_collection_name].insert_one(jsonable_encoder(booking))
    await update_points(db, user, package['reward_points'])
    booking_details= await db[booking_collection_name].find_one(book.inserted_id)
    return booking_details

async def edit_social_media(db,artist: EditSocialMedia, user):
    artist = {k: v for k, v in artist.dict().items() if v is not None}
    artist_check= await db[collection_name].find_one({'user_id': user})
    if artist_check is None:
        raise HTTPException(status_code=404, detail=f"artist not found")
    social_id= artist_check['social_accounts']
    if len(artist) >= 1:

        update_result = await db[social_media_collection_name].update_one(
            {"_id": social_id}, {"$set": artist}
        )

        if update_result.modified_count == 1:
            if (
                updated_artist := await db[social_media_collection_name].find_one({"_id": social_id})
            ) is not None:
                return updated_artist

    if (
        existing_artist := await db[social_media_collection_name].find_one({"_id": social_id})
    ) is not None:
        return existing_artist

    raise HTTPException(status_code=404, detail=f"Social Media with id {social_id} not found")

async def check_seats_on_date(db, book_date, package):
    bookings= await db[booking_collection_name].find({'package_id': package},     ).to_list(10000)
    booking_of_date=[]
    for i in bookings:
        if datetime.fromisoformat(i['booking_time']).replace(tzinfo=timezone.utc).date() ==book_date :
            booking_of_date.append(i)
    seats= sum([booking['seats'] for booking in booking_of_date])
    return seats

async def update_points(db, user, point_to_add):
    print('--------------- ', user)
    point_detail= await db[points_collection_name].find_one({'user':user})
    point= point_detail['points']
    check= await db[points_collection_name].update_one({'user':user},{'$set': {'points': point+point_to_add}})


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
    pipeline= get_pipeline_for_notification(review.venue)
    venue =await db[collection_name].aggregate(pipeline).to_list(12)
    return venue

async def get_venue_review(db, id,page):
    venue= await check_venue_exists(db, id)
    pipeline= get_venue_review_pipeline(id, page)  
    reviews =await db[review_collection_name].aggregate(pipeline).to_list(5)
    return reviews

async def get_venue_package(db,page,limit, type,user):  
    venue= await get_venue_by_userid(db, user)
    if type==0:
        packages=await db[package_collection_name].find({'venue_id': venue['_id'], 'valid':True}).skip((page-1)*limit).limit(limit).to_list(limit+1)
    else:
        packages=await db[package_collection_name].find({'venue_id': venue['_id'], 'valid':False}).skip((page-1)*limit).limit(limit).to_list(limit+1)
    return packages

async def get_venue_schedule(db,page,limit,user):  
    venue= await get_venue_by_userid(db, user)
    schedule= await db[schedule_collection_name].find({'venue': venue['_id']}).skip((page-1)*limit).limit(limit).to_list(limit+1)
    return schedule


async def feature_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_featured': True}})
    print(result.modified_count)
    if result.modified_count==1:
        return {'success'}
    

async def invalid_package(db,id, user):
    await check_package_belongs_to_venue(db, id, user)
    result= await db[package_collection_name].update_one({'_id': id}, {'$set': {'valid': False}})
    return {"success":True}

async def unfeature_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_featured': False}})
    print(result)
    return {"success":True}

async def verify_venue(db,id):
    await check_venue_exists(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_verified': True}})
    print(result)
    return {"success":True}

async def unverify_venue(db,id):
    await get_venue_byid(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_verified': False}})
    print(result)
    return {"success":True}

async def complete_booking(db,id, user):
    venue= await get_venue_by_userid(db, user)
    booking= await db[booking_collection_name].find_one({'_id': id})
    if booking is None or booking['venue_id']!= venue['_id']:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking not found")
    result= await db[booking_collection_name].update_one({'_id': id}, {'$set': {'complete': True}})
    print(result)
    return {"success":True}

def get_featured_pipeline(page):
    return [
        {
            "$match": {
                "is_featured": True
            }
        },
  {
            "$lookup": {
                "from": "VenueReview",
                "localField": "_id",
                "foreignField": "venue",
                "as": "reviews"
            }
        },
       {
            "$addFields": {
                "average_rating": {
                    "$ifNull": [
                        {"$avg": "$reviews.rating"},
                        0
                    ]
                }
            }
        },
        {
            "$unset": "reviews"  
        },
  
  
  {
      "$sort":{
          
          "_id":1,
      }
  },
  {
    "$skip": (page-1)*12
  },
  {
    "$limit": 12
  }
]

def get_pipeline(page):
    return [
        {
            "$match": {
                "is_verified": True
            }
        },
  {
            "$lookup": {
                "from": "VenueReview",
                "localField": "_id",
                "foreignField": "venue",
                "as": "reviews"
            }
        },
       {
            "$addFields": {
                "average_rating": {
                    "$ifNull": [
                        {"$avg": "$reviews.rating"},
                        0
                    ]
                }
            }
        },
        {
            "$unset": "reviews"  
        },
  
  
  {
      "$sort":{
          "is_featured":-1,
          "_id":1,
      }
  },
  {
    "$skip": (page-1)*12
  },
  {
    "$limit": 12
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
            "$lookup": {
                "from": "VenueReview",
                "localField": "_id",
                "foreignField": "venue",
                "as": "reviews"
            }
        },
       {
            "$addFields": {
                "average_rating": {
                    "$ifNull": [
                        {"$avg": "$reviews.rating"},
                        0
                    ]
                }
            }
        },
        {
            "$unset": "reviews"  
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
            "$lookup": {
                "from": "VenueReview",
                "localField": "_id",
                "foreignField": "venue",
                "as": "reviews"
            }
        },
       {
            "$addFields": {
                "average_rating": {
                    "$ifNull": [
                        {"$avg": "$reviews.rating"},
                        0
                    ]
                }
            }
        },
        {
            "$unset": "reviews"  
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
            "$unwind": "$package_details"
        },
  {
            "$match": {
                "package_details.valid": True
            }
        },
  {
    "$lookup": {
      "from": "SocialMedia",
      "localField": "social_accounts",
      "foreignField": "_id",
      "as": "social_accounts"
    }
  },

  
 {
    "$unwind": {
      "path": "$package_details",
      "preserveNullAndEmptyArrays": True
    }
  },
#   {
#     "$match": {
#       "package_details.valid": True
#     }
#   },
  {
    "$group": {
      "_id": "$_id",
      "alias": {
        "$first": "$alias"
      },
      "location": {
        "$first": "$location"
      },
      "description": {
        "$first": "$description"
      },
      "category": {
        "$first": "$category"
      },
      "images": {
        "$first": "$images"
      },
      "is_featured": {
        "$first": "$is_featured"
      },
      "is_verified": {
        "$first": "$is_verified"
      },
      "menu": {
        "$first": "$menu"
      },
      "video": {
        "$first": "$video"
      },
      "package_details": {
        "$push": "$package_details"
      },
      "social_accounts": {
        "$push": "$social_accounts"
      }
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
      "from": "BookingTransaction",
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
                "email": "$user_details.email",
                "phone_no": "$user_details.phone_no",
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


def get_pipeline_for_notification(id):
    return [
        {
            "$match": {
                "_id": id
            }
        },
  {
            "$lookup": {
                "from": "VenueReview",
                "localField": "_id",
                "foreignField": "venue",
                "as": "reviews"
            }
        },
       {
            "$addFields": {
                "average_rating": {
                    "$ifNull": [
                        {"$avg": "$reviews.rating"},
                        0
                    ]
                }
            }
        },
        {
            "$unset": "reviews"  
        },
  
  
]
