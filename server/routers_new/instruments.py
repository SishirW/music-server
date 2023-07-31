from fastapi import APIRouter, Request, Depends, HTTPException, status
from server.schemas import ShowUser
from server.routers.user import validate_admin, validate_user
from server.schemas_new.instruments import AddInstrumentSchema, UpdateInstrumentSchema
from server.models.instuments import add_new_instrument, delete_instrument_by_id, find_instrument_by_id, find_all_insturments, get_total_instrument_count
from fastapi.encoders import jsonable_encoder


from server.db import get_database

router = APIRouter(prefix="/instruments", tags=["Instruments"])


@router.get('/')
async def get_instruments(request: Request, page=1, limit=5, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await find_all_insturments(db, int(page), int(limit))
    return jsonable_encoder(result)


@router.get('/count')
async def get_total_instruments_count(request: Request, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await get_total_instrument_count(db)
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_instrument_by_id(id: str, request: Request, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await find_instrument_by_id(db, id)
    return jsonable_encoder(result)


@router.post('/')
async def add_instrument(request: Request, instrument: AddInstrumentSchema, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    result = await add_new_instrument(db, instrument)
    return jsonable_encoder(result)
    # return result


@router.delete('/{id}')
async def delete_instrument(id: str, request: Request, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    result = await delete_instrument_by_id(db, id)
    return jsonable_encoder(result)


# @router.put('/{id}')
# async def delete_instrument(id: str, request: Request, instrument: UpdateInstrumentSchema, current_user: ShowUser = Depends(validate_admin)):
#     db = get_database(request)
#     result = await delete_instrument_by_id(db, id)
#     return jsonable_encoder(result)
