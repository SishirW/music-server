from . import BaseModel, PydanticBaseModel, PyObjectId, Image, Review
from typing import List, Optional
from pydantic import EmailStr, Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid
import shutil,os

collection_name= 'Artist'

class Skill(BaseModel):
    skill: str

class Genre(BaseModel):
    genre: str

class ArtistSchedule(BaseModel):
    artist: PyObjectId= Field(...)
    venue: PyObjectId= Field(...)
    start_time: datetime
    end_time: datetime

class ArtistFollow(BaseModel):
    artist: PyObjectId= Field(...)
    user: PyObjectId= Field(...)

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
    print(encoded)
    await db[collection_name].insert_one(encoded)
    # new_user = await find_band_by_id(db, str(bnd.id), user)
    # return new_band
    return {'success': True}

async def get_artist_by_userid(db, id):
    artist = await db[collection_name].find_one({"user_id": id})
    print(artist)
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"artist not found!")
    return artist

async def get_artist_byid(db, id):
    artist = await db[collection_name].find_one({"_id": id})
    print(artist)
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"artist not found!")
    return artist

async def get_relevant_artist(db,page):
    artist = db[collection_name].find().skip((page-1)*5).limit(5)
    artists=[]
    async for a in artist:
        artists.append(a)
    print(artist)
    return artists

async def get_featured_artist(db,page):
    artist = db[collection_name].find().sort(
            [('featured', -1)]).skip((page-1)*5).limit(5)
    artists=[]
    async for a in artist:
        artists.append(a)
    print(artist)
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
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')
