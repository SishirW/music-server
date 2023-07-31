from typing import List
from urllib import response
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from ..schemas import AddToCart, ShowCart, ShowProduct, ShowProductCart, ShowUser
from .user import get_current_user

router = APIRouter(prefix="/cart", tags=["Product Cart"])


@router.put('/')
async def add_to_cart(request: Request, product_to_add: AddToCart, current_user: ShowUser = Depends(get_current_user)):
    id = product_to_add.product_id
    quantity = product_to_add.quantity
    product = await request.app.mongodb['Products'].find_one({"_id": product_to_add.product_id})
    if product is None:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_to_add.product_id} not found")
    product_to_add = jsonable_encoder(product_to_add)
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
    for data in user['cart']:
        if data['product_id'] == id:
            original_quantity = data['quantity']
            await request.app.mongodb['Users'].update_one({'_id': current_user['_id'], 'cart.product_id': id}, {'$set': {'cart.$.quantity': quantity+original_quantity}})
            return {"Successfully updated cart"}
    await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push': {'cart': product_to_add}})
    return {"Successfully added to cart"}


@router.get('/', response_model=List[ShowProductCart])
async def get_cart(request: Request, current_user: ShowUser = Depends(get_current_user)):
    cart = []
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
    if 'cart' not in user:
        user = await request.app.mongodb['Users'].update_one({"_id": current_user['_id']}, {'$push': {'cart': None}})
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})

    if len(user['cart']) >= 1:
        for data in user['cart']:
            a = await request.app.mongodb['Products'].find_one({"_id": data['product_id']})
            if a is not None:
                a['quantity'] = data['quantity']
                cart.append(a)
        if len(cart) == 0:
            return []
        return cart
    return []


@router.delete('/')
async def delete_cart(request: Request, id: str, current_user: ShowUser = Depends(get_current_user)):
    update_result = await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$pull': {'cart': {"product_id": id}}})
    print(update_result.modified_count)
    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"success": True}
