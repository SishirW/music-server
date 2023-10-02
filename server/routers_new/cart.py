from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile
from typing import List
from fastapi.encoders import jsonable_encoder
from server.db import get_database
from server.schemas_new.cart import AddToCart
from ..utils.user import  validate_admin, get_current_user
from server.schemas import ShowUserWithId
from server.models.cart import create_cart, get_relevant_cart,delete_cart
router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post('/')
async def add_to_cart(request: Request, cart: AddToCart, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await create_cart(db, cart,current_user['_id'])
    return jsonable_encoder(result)


@router.get('/',)
async def get_relevant_carts(request: Request, page: int = 1, limit: int=5, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await get_relevant_cart(db,page, limit,current_user['_id'])
    return jsonable_encoder(result)

@router.delete('/', response_description='Delete artist schedule',status_code=status.HTTP_204_NO_CONTENT)
async def delete_from_cart(request: Request, product_id: str, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result=await delete_cart(db, product_id, current_user['_id'])
    return jsonable_encoder(result)

