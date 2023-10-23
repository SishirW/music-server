from fastapi import APIRouter, Request, Depends, HTTPException, status
from server.schemas import ShowUser
from ..utils.user import validate_artist, validate_admin
from server.schemas_new.bands import AddBandSchema
from server.models.bands import add_new_band, find_all_bands, get_total_band_count, find_band_by_id, delete_band_by_id, find_all_bands_for_a_user
from fastapi.encoders import jsonable_encoder

from server.utils.location import get_location_from_header

from server.models.applications import create_new_application, change_band_application_status

from server.db import get_database

router = APIRouter(prefix="/bands", tags=["Bands"])


@router.get('/')
async def get_bands(request: Request, page=1, limit=5,  current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    location = get_location_from_header(request)
    result = await find_all_bands(db, current_user, location, int(page), int(limit))
    return jsonable_encoder({"bands": result})


@router.get('/my-listings')
async def get_my_bands(request: Request, page=1, limit=5,  current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await find_all_bands_for_a_user(db, current_user, int(page), int(limit))
    return jsonable_encoder(result)


@router.post('/')
async def add_band(request: Request, band: AddBandSchema, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    location = get_location_from_header(request)
    result = await add_new_band(db, band, location, current_user)
    return jsonable_encoder(result)


@router.get('/count')
async def get_total_bands_count(request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await get_total_band_count(db)
    return jsonable_encoder({"count": result})


@router.get('/{id}')
async def get_band_by_id(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await find_band_by_id(db, id, current_user)
    return jsonable_encoder(result)


@router.delete('/{id}')
async def delete_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await delete_band_by_id(db, id)
    return jsonable_encoder(result)


# @router.put('/{id}')
# async def edit_band(id: str, band: AddBandSchema, request: Request, current_user: ShowUser = Depends(validate_artist)):
#     db = get_database(request)
#     # result = await update(db, id)
#     return jsonable_encoder({"data": "Band Updated"})


@router.get('/{id}/apply')
async def apply_to_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    await create_new_application(db, id, current_user['_id'])
    return jsonable_encoder({"data": "Applied to the band!"})


@router.get('/application/{id}/accept')
async def accept_application_to_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    await change_band_application_status(db, id, 1)
    return jsonable_encoder({"data": "Accepted Request!"})


@router.get('/application/{id}/reject')
async def reject_application_to_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    await change_band_application_status(db, id, -1)
    return jsonable_encoder({"data": "Rejected Request!"})
