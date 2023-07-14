from fastapi import APIRouter, Request, Depends, HTTPException, status
from server.schemas import ShowUser
from server.routers.user import validate_artist, validate_admin
from server.schemas_new.bands import AddBandSchema
from server.models.bands import add_new_band, find_all_bands, get_total_band_count, find_band_by_id, delete_band_by_id
from fastapi.encoders import jsonable_encoder


from server.db import get_database

router = APIRouter(prefix="/bands", tags=["Bands"])


@router.get('/')
async def get_bands(request: Request, page=1, limit=5):
    db = get_database(request)
    result = await find_all_bands(db, int(page), int(limit))
    return jsonable_encoder(result)


@router.post('/')
async def add_band(request: Request, band: AddBandSchema, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await add_new_band(db, band, current_user)
    return jsonable_encoder(result)


@router.get('/count')
async def get_total_bands_count(request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await get_total_band_count(db)
    return jsonable_encoder({"count": result})


@router.get('/{id}')
async def get_band_by_id(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await find_band_by_id(db, id)
    return jsonable_encoder(result)


@router.delete('/{id}')
async def delete_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    result = await delete_band_by_id(db, id)
    return jsonable_encoder(result)


@router.put('/{id}')
async def edit_band(id: str, band: AddBandSchema, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    # result = await update(db, id)
    return jsonable_encoder({"data": "Band Updated"})


@router.get('/{id}')
async def apply_to_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    # result = await update(db, id)
    return jsonable_encoder({"data": "Couldn't apply to band"})


@router.get('/{id}')
async def accept_application_to_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    # result = await update(db, id)
    return jsonable_encoder({"data": "Accepted Request!"})


@router.get('/{id}')
async def reject_application_to_band(id: str, request: Request, current_user: ShowUser = Depends(validate_artist)):
    db = get_database(request)
    # result = await update(db, id)
    return jsonable_encoder({"data": "Rejected Request!"})
