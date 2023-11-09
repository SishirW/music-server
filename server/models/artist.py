from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr, Field, HttpUrl
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid
import shutil,os
from server.schemas_new.artist import CreateScheduleSchema, EditScheduleSchema, FollowArtistSchema, EditArtistSchema, EditSocialMedia
from ..models.instuments import check_instrument_exists
from ..models.genres import check_genre_exists
from .venue import SocialMedia, social_media_collection_name, user_collection_name
collection_name= 'Artist'
schedule_collection_name= 'ArtistSchedule'
follow_collection_name= 'ArtistFollow'
skill_collection_name= 'Instruments'


class Skill(BaseModel):
    skill: str

class Genre(BaseModel):
    genre: str

class ArtistSchedule(BaseModel):
    artist: str= Field(...)
    venue: Optional[str]
    description: str
    start_time: datetime
    end_time: datetime

class ArtistFollow(BaseModel):
    artist: str= Field(...)
    user: str= Field(...)

class Artist(BaseModel):
    alias: str
    description: str
    skills: List[str] =[]
    genre: List[str] =[]
    looking_for: List[str]=[]
    images: List[str]=[]
    is_featured: bool= False
    location: str
    video: HttpUrl= None
    user_id: str= Field(...)
    social_accounts: str


async def add_artist(db, artist, user):
    skills= [x for x in artist.skills if await check_instrument_exists(x,db)]
    genre= [x for x in artist.genre if await check_genre_exists(x,db)]
    social= SocialMedia(
        facebook= artist.social_media.facebook,
        instagram= artist.social_media.instagram,
        youtube= artist.social_media.youtube,
        tiktok= artist.social_media.tiktok,
    )
    social_encoded= jsonable_encoder(social)
    social_media_detail= await db[social_media_collection_name].insert_one(social_encoded)
    social_media_id= social_media_detail.inserted_id
    artist1 = Artist(
        alias= artist.alias,
        description= artist.description,
        skills= skills,
        genre= genre,
        user_id= user,
        location=artist.location,
        looking_for=artist.looking_for,
        video= artist.video,
        social_accounts= social_media_id
    )
    encoded = jsonable_encoder(artist1)
    insert_artist= await db[collection_name].insert_one(encoded)
    detail= await db[collection_name].find_one({'_id': insert_artist.inserted_id})
    return detail
    return {'success': True}

async def edit_artist(db,artist: EditArtistSchema, user):
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

    raise HTTPException(status_code=404, detail=f"Artist with id {artist_id} not found")

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

async def get_artist_by_userid(db, id):
    artist = await db[collection_name].find_one({"user_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Artist not found!")
    return artist

async def get_artist_info(db, id):
    artist = await db[collection_name].find_one({"_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Artist not found!")
    return artist


async def get_artist_byid(db, id, user_id):
    pipeline= get_artist_detail_pipeline(id, user_id) 
    artist =await db[collection_name].aggregate(pipeline).to_list(10)
    if artist==[]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"artist not found!")
    
    return artist

async def check_artist_exists(db, id):
    artist = await db[collection_name].find_one({"_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"artist not found!")
    return artist
  

async def get_relevant_artist(db,page,genre, search, searchtype,user_id):
    if searchtype==1 and search!=None:
        skills = await db[skill_collection_name].find_one({'name': {
                                                    "$regex": f".*{search}.*", '$options': 'i'}})
        print(skills)
        search= skills["_id"]
    if search != None:
        pipeline= get_search_pipeline(search, user_id, page, searchtype)  # 0 for search by name. 1 for search by instrument
        artist =await db[collection_name].aggregate(pipeline).to_list(5)
    elif genre != None:
        pipeline= get_genre_pipeline(genre, user_id, page)
        artist =await db[collection_name].aggregate(pipeline).to_list(5)
    else:
      pipeline= get_pipeline(user_id, page)
      artist =await db[collection_name].aggregate(pipeline).to_list(5)
    return artist

async def get_featured_artist(db,page):
    artist = db[collection_name].find().sort(
            [('featured', -1)]).skip((page-1)*5).limit(5).to_list(5)
    return artist

async def add_images(db,artist_id, files):
    names = []
    if files is not None:
        for file in files:
            image_name = uuid.uuid4()
            os.makedirs(f'media_new/artist/{artist_id}', exist_ok=True)
            with open(f"media_new/artist/{artist_id}/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            names.append(f"{image_name}.png")
        db[collection_name].update_one({'_id': artist_id}, {'$push': {'images': {'$each':names}}})
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')

async def add_schedule(db,schedule: CreateScheduleSchema,user_id):
    artist= await get_artist_by_userid(db, user_id)
    sch= ArtistSchedule(
        artist= artist['_id'],
        venue= schedule.venue,
        description= schedule.description,
        start_time= schedule.start_time,
        end_time= schedule.end_time
    )
    encoded = jsonable_encoder(sch)
    await db[schedule_collection_name].insert_one(encoded)
    return {'success': True}

async def get_artist_schedule(db,page,limit,user):  
    artist= await get_artist_by_userid(db, user)
    schedule= await db[schedule_collection_name].find({'artist': artist['_id']}).skip((page-1)*limit).limit(limit).to_list(limit+1)
    return schedule


async def check_schedule_belongs_to_artist(db,schedule_id, user_id):
    schedule= await db[schedule_collection_name].find_one({"_id": schedule_id})
    if schedule is None:
        raise HTTPException(status_code=404, detail=f"schedule not found")
    artist=await get_artist_by_userid(db,user_id)
    return schedule['artist']== artist['_id']


async def edit_schedule(db,schedule_id,schedule: EditScheduleSchema, user):
    schedule = {k: v for k, v in schedule.dict().items() if v is not None}
    check= await check_schedule_belongs_to_artist(db, schedule_id, user)
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

async def delete_schedule(db, schedule_id, user):
    check= await check_schedule_belongs_to_artist(db, schedule_id, user)
    if not check:
        raise HTTPException(status_code=404, detail=f"Schedule not found")
    schedule=await db[schedule_collection_name].delete_one({'_id': schedule_id})
    if schedule.deleted_count == 1:
        return {f"Successfully deleted schedule"}
    else:
        raise HTTPException(status_code=404, detail=f"schedule not found")


async def delete_images(db, id, files):
    empty=[]
    for image in files:
        update_result= await db[collection_name].update_one({'_id': id}, {'$pull': {'images': image}})
        if update_result.modified_count == 0:
            empty.append(image)
    if len(empty) == 0:
        return {"detail": "Successfully deleted image", "not_found": []}
    else:
        return {"detail": "Some images were missing", "not_found": empty}

async def delete_artist(db, id):
    check= await check_artist_exists(db, id)

    if not check:
        raise HTTPException(status_code=404, detail=f"Artist not found")
    artist= await db[collection_name].find_one({'_id': id})
    deleted_artist=await db[collection_name].delete_one({'_id': id})
    await db[user_collection_name].update_one({"_id": artist['user_id']}, {"$set": {'type': 'user'}})
    if deleted_artist.deleted_count == 1:
        return {f"Successfully deleted artist"}
    else:
        raise HTTPException(status_code=404, detail=f"Package not artist")

async def follow_artist(db, user, follow: FollowArtistSchema):
    artist= await check_artist_exists(db, follow.artist)
    if artist['user_id']== user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Cant follow yourself")
    query= {"$and": [
        {"artist": artist['user_id']},
        {"user": user}
    ]}
    check_followed= await db[follow_collection_name].find_one(query)
    if check_followed is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Already followed this artist")
    follow= ArtistFollow(
        artist= artist['user_id'],
        user= user
    )
    encoded = jsonable_encoder(follow)
    await db[follow_collection_name].insert_one(encoded)
    return {'success': True}

async def unfollow_artist(db, user, follow: FollowArtistSchema):
    artist= await check_artist_exists(db, follow.artist)
    query= {"$and": [
        {"artist": artist['user_id']},
        {"user": user}
    ]}
    check_followed= await db[follow_collection_name].delete_one(query)
    if check_followed.deleted_count == 1:
        return {f"Unfollowed"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Not a follower")

async def feature_artist(db,id):
    await check_artist_exists(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_featured': True}})
    print(result)
    return {"success":True}

async def unfeature_artist(db,id):
    await check_artist_exists(db, id)
    result= await db[collection_name].update_one({'_id': id}, {'$set': {'is_featured': False}})
    print(result)
    return {"success":True}

async def get_followers_count(db, artist_id):
    artist=await check_artist_exists(db, artist_id)
    artist_user_id= artist['user_id']
    pipeline= [
  {
    "$match": {
      "_id": artist_id
    }
  },
  {
    "$lookup": {
      "from": "ArtistFollow",
      "localField": "user_id",
      "foreignField": "artist",
      "as": "artist_followers"
    }
  },
  {
    "$addFields": {
      "followers_count": {
        "$size": "$artist_followers"
      }
    }
  },
  {
    "$project": {
      "_id": 0,
      "followers_count": 1
    }
  }
]
    count= await db[collection_name].aggregate(pipeline).to_list(5)
    return count

async def get_follower(db, artist_id,page,user_id):
    artist=await check_artist_exists(db, artist_id)
    artist_user_id= artist['user_id']
    pipeline= [
  {
    "$match": {
      "artist": artist_user_id
    }
  },
  {
    "$lookup": {
      "from": "Artist",
      "localField": "user",
      "foreignField": "user_id",
      "as": "artist_detail"
    }
  },
  {
    "$lookup": {
      "from": "ArtistFollow",
      "localField": "user",
      "foreignField": "artist",
      "as": "artist_followers"
    }
  },
  {
    "$addFields": {
      "isFollowedByUser": {
        "$in": [
          user_id,
          "$artist_followers.user"
        ]
      }
    }
  },
  {
    "$project": {
      "_id": 0,
      "artist_detail": "$artist_detail",
      "following": "$isFollowedByUser"
    },
    
  },
  {
    "$skip": (page-1)*5
  },
  {
    "$limit": 5
  }

]
    followers= await db[follow_collection_name].aggregate(pipeline).to_list(5)
    return followers



async def get_following(db, artist_id,page,user_id):
    artist=await check_artist_exists(db, artist_id)
    artist_user_id= artist['user_id']
    pipeline= [
  {
    "$match": {
      "user": artist_user_id
    }
  },
  {
    "$lookup": {
      "from": "Artist",
      "localField": "artist",
      "foreignField": "user_id",
      "as": "artist_detail"
    }
  },
  {
    "$lookup": {
      "from": "ArtistFollow",
      "localField": "artist",
      "foreignField": "artist",
      "as": "artist_followers"
    }
  },
  {
    "$addFields": {
      "isFollowedByUser": {
        "$in": [
          user_id,
          "$artist_followers.user"
        ]
      }
    }
  },
  {
    "$project": {
      "_id": 0,
      "artist_detail": "$artist_detail",
      "following": "$isFollowedByUser"
    }
  },
  {
    "$skip": (page-1)*5
  },
  {
    "$limit": 5
  }
]
    following= await db[follow_collection_name].aggregate(pipeline).to_list(5)
    return following


def get_pipeline(user_id, page):
    return [
  {
    "$lookup": {
      "from": "ArtistFollow",
      "localField": "user_id",
      "foreignField": "artist",
      "as": "artist_followers"
    }
  },
  {
    "$addFields": {
      "isFollowedByUser": {
        "$in": [
          user_id,
          "$artist_followers.user"
        ]
      },
      
    }
  },
  {
    "$unset": ["artist_followers",]
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

def get_search_pipeline(keyword,user_id, page, type):
    pipeline_term= "alias" if type==0 else "skills"
    
    return [
      {
  "$match": {
    pipeline_term: {
      "$regex": f".*{keyword}.*",
      "$options": "i"
    }
  }
  },
  {
  "$lookup": {
    "from": "ArtistFollow",
    "localField": "user_id",
    "foreignField": "artist",
    "as": "artist_followers"
  }
  },
  
  
  {
  "$addFields": {
    "isFollowedByUser": {
      "$in": [
        user_id,
        "$artist_followers.user"
      ]
    },
  }
  },
  {
  "$unset": ["artist_followers",]
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
  
  

def get_genre_pipeline(genre,user_id, page):
    return [
     {
            "$match": {
                "genre": {
                    "$in": [genre]
                }
            }
        },
  {
  "$lookup": {
    "from": "ArtistFollow",
    "localField": "user_id",
    "foreignField": "artist",
    "as": "artist_followers"
  }
  },
  
  
  {
  "$addFields": {
    "isFollowedByUser": {
      "$in": [
        user_id,
        "$artist_followers.user"
      ]
    },
  }
  },
  {
  "$unset": ["artist_followers", "artist_following"]
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
    

def get_artist_detail_pipeline(id,user_id):
    return [
     {
            "$match": {
                "_id": id
            }
        },
  {
  "$lookup": {
    "from": "ArtistFollow",
    "localField": "user_id",
    "foreignField": "artist",
    "as": "artist_followers"
  }
  },
  {
  "$lookup": {
    "from": "ArtistFollow",
    "localField": "user_id",
    "foreignField": "user",
    "as": "artist_following"
  }
  },
  {
    "$lookup": {
      "from": "ArtistSchedule",
      "localField": "_id",
      "foreignField": "artist",
      "as": "schedule_details"
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
  "$addFields": {
    "isFollowedByUser": {
      "$in": [
        user_id,
        "$artist_followers.user"
      ]
    },
    "followers_count": {
      "$size": "$artist_followers"
    },
    "following_count": {
      "$size": "$artist_following"
    }
  }
  },
  {
  "$unset": ["artist_followers", "artist_following"]
  },
  
]