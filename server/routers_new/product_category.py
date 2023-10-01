from fastapi import APIRouter, Request, Depends, HTTPException, status
from server.schemas import ShowUser
from server.routers.user import validate_admin, validate_user
from server.schemas_new.productcategory import AddProductCategorySchema
from server.models.product_category import add_new_productcategory, delete_productcategory_by_id, find_all_productcategorys, find_productcategory_by_id, get_total_productcategory_count
from fastapi.encoders import jsonable_encoder


from server.db import get_database

router = APIRouter(prefix="/productcategory", tags=["ProductCategory"])


@router.get('/')
async def get_productcategory(request: Request, page=1, limit=5, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await find_all_productcategorys(db, int(page), int(limit))
    return jsonable_encoder(result)


@router.get('/count')
async def get_total_productcategory_count(request: Request, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await get_total_productcategory_count(db)
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_productcategory_by_id(id: str, request: Request, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await find_productcategory_by_id(db, id)
    return jsonable_encoder(result)


@router.post('/')
async def add_productcategory(request: Request, genre: AddProductCategorySchema, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    print("result", end='\n'*7)
    result = await add_new_productcategory(db, genre)
    print(dir(result), end='\n'*7)
    print("result", end='\n'*7)
    return jsonable_encoder(result)


@router.delete('/{id}')
async def delete_productcategory(id: str, request: Request, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    result = await delete_productcategory_by_id(db, id)
    return jsonable_encoder(result)


