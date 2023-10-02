from fastapi import APIRouter, Request, Depends, HTTPException, status
from server.schemas import ShowUser
from ..utils.user import validate_admin, get_current_user
from server.schemas_new.venuecategory import AddVenueCategorySchema
from server.models.venue_category import add_new_venuecategory, delete_venuecategory_by_id, find_all_venuecategorys, find_venuecategory_by_id, get_total_venuecategory_count
from fastapi.encoders import jsonable_encoder


from server.db import get_database

router = APIRouter(prefix="/venuecategory", tags=["VenueCategory"])


@router.get('/')
async def get_venuecategory(request: Request, page=1, limit=5, current_user: ShowUser = Depends(get_current_user)):
    db = get_database(request)
    result = await find_all_venuecategorys(db, int(page), int(limit))
    return jsonable_encoder(result)


@router.get('/count')
async def get_total_venuecategory_count(request: Request, current_user: ShowUser = Depends(get_current_user)):
    db = get_database(request)
    result = await get_total_venuecategory_count(db)
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_venuecategory_by_id(id: str, request: Request, current_user: ShowUser = Depends(get_current_user)):
    db = get_database(request)
    result = await find_venuecategory_by_id(db, id)
    return jsonable_encoder(result)


@router.post('/')
async def add_venuecategory(request: Request, genre: AddVenueCategorySchema, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    print("result", end='\n'*7)
    result = await add_new_venuecategory(db, genre)
    print(dir(result), end='\n'*7)
    print("result", end='\n'*7)
    return jsonable_encoder(result)


@router.delete('/{id}')
async def delete_venuecategory(id: str, request: Request, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    result = await delete_venuecategory_by_id(db, id)
    return jsonable_encoder(result)


