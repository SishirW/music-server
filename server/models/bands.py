from __future__ import annotations
from . import BaseModel, PydanticBaseModel
from typing import List, Optional
from fastapi import HTTPException, status

from fastapi.encoders import jsonable_encoder
from server.schemas_new.bands import AddBandSchema

from server.utils.location import get_distance
from server.models.applications import find_applications_for_a_band

from . import BaseModel

collection_name = "Bands"


class Geometry(PydanticBaseModel):
    type: str
    coordinates: List[float]


class Properties(PydanticBaseModel):
    category: str = "Point"
    name: str


class Location(PydanticBaseModel):
    type: str
    geometry: Geometry
    properties: Properties


class Band(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    genres: Optional[List[str]] = None
    location: Location
    created_by: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


async def get_total_band_count(db):
    count = await db[collection_name].count_documents({})
    return count


async def get_relevant_band_count(db):
    count = await db[collection_name].count_documents({})
    return count


async def add_new_band(db, band: AddBandSchema, location, user):
    location = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [location['long'], location['lat']]},
        "properties": {
            "category": "Stadiums",
            "name": user['username']
        }
    }
    bnd = Band(
        name=band.name, genres=band.genres, description=band.description, location=location, created_by=user['username'])
    encoded = jsonable_encoder(bnd)
    await db[collection_name].insert_one(encoded)
    new_band = await find_band_by_id(db, str(bnd.id), user)
    return new_band


async def find_band_by_id(db, id, current_user):
    band = await db[collection_name].find_one({"_id": id})
    if band is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"band not found!")
    band_creator = await db['Users'].find_one({'username': band['created_by']})
    artist_profile = await db['Artist'].find_one({'artist_id': band_creator['_id']})
    band['artist'] = artist_profile
    if current_user['username'] == band['created_by']:
        band['applications'] = await find_applications_for_a_band(db, id)

    return band


async def delete_band_by_id(db, id):
    deleted_band = await db[collection_name].delete_one({'_id': id})
    if deleted_band.deleted_count == 1:
        return {f"Successfully deleted band with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"band not found!")


async def find_all_bands(db, user, location, page, limit):
    # bands = await db[collection_name].find().skip(
    #     (page-1)*limit).limit(limit).to_list(limit+1)
    lat = location['lat']
    long = location['long']
    bands = await find_relevant_bands(db, user, lat, long, page, limit)
    return bands


async def find_all_bands_for_a_user(db, user, page, limit):
    bands = await db[collection_name].find({
        'created_by': user['username']
    }).skip(
        (page-1)*limit).limit(limit).to_list(limit+1)
    return bands


async def find_relevant_bands(db, user, lat, long, page, limit):

    bands = await db[collection_name].find({
        'created_by': {'$ne': user['username']},
        'location.geometry': {
            '$near': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': [
                        long, lat
                    ]
                },
                '$minDistance': 0,
                '$maxDistance': 1000000
            }
        }
    }).skip(
        (page-1)*limit).limit(limit).to_list(limit+1)
    for band in bands:
        lon2, lat2 = band['location']['geometry']['coordinates']
        band['distance'] = get_distance(lat, long, lat2, lon2)
        band_creator = await db['Users'].find_one({'username': band['created_by']})
        artist_profile = await db['Artist'].find_one({'artist_id': band_creator['_id']})
        band['artist'] = artist_profile
    return bands

    # async def update_band(db,id,data):
    #     band
