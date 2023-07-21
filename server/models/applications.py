from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import Optional

from . import BaseModel, PydanticBaseModel

collection_name = "BandApplications"


class BandApplication(BaseModel):
    band_id: str
    artist_id: str
    status: int = 0


async def create_new_application(db, band_id, artist_id):
    new_application = BandApplication(band_id=band_id, artist_id=artist_id)
    encoded = jsonable_encoder(new_application)
    await db[collection_name].insert_one(encoded)
    new_band = await find_band_application_by_id(db, str(new_application.id))
    return new_band


async def find_applications_for_a_band(db, band_id):
    band_application = await db[collection_name].find({"band_id": band_id}).to_list(100)
    if band_application is None:
        return []
    return band_application


async def find_band_application_by_id(db, id):
    band_application = await db[collection_name].find_one({"_id": id})
    if band_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Band Application not found!")
    return band_application


async def change_band_application_status(db, id, status):
    band_application = await db[collection_name].find_one({"_id": id})
    if band_application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Band Application not found!")
    result = await db[collection_name].update_one(
        {'_id': id},
        {'$set': {"status": status}}
    )
    return result
