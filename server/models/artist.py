from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr, Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid
import shutil,os
from server.schemas_new.artist import CreateScheduleSchema, EditScheduleSchema

collection_name= 'Artist'
schedule_collection_name= ' ArtistSchedule'

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
    #location: str = Field(...)
    description: str
    skills: List[str] =[]
    genre: List[str] =[]
    images: List[str]=[]
    is_featured: bool= False
    #video: Optional[str]
    user_id: str= Field(...)


async def add_artist(db, artist, user):
    artist1 = Artist(
        alias= artist.alias,
        description= artist.description,
        skills= artist.skills,
        genre= artist.genre,
        user_id= user,
    )
    encoded = jsonable_encoder(artist1)
    await db[collection_name].insert_one(encoded)
    # new_user = await find_band_by_id(db, str(bnd.id), user)
    # return new_band
    return {'success': True}

async def get_artist_by_userid(db, id):
    artist = await db[collection_name].find_one({"user_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"artist not found!")
    return artist

async def get_artist_byid(db, id):
    artist = await db[collection_name].find_one({"_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"artist not found!")
    return artist

async def get_relevant_artist(db,page):
    artist = db[collection_name].find().skip((page-1)*5).limit(5)
    artists=[]
    async for a in artist:
        artists.append(a)
    return artists

async def get_featured_artist(db,page):
    artist = db[collection_name].find().sort(
            [('featured', -1)]).skip((page-1)*5).limit(5)
    artists=[]
    async for a in artist:
        artists.append(a)
    return artists

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