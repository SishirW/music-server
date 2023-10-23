from . import BaseModel
from typing import List
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from .products import check_product_exists
from server.schemas_new.cart import AddToCart


collection_name= 'Cart'

class Cart(BaseModel):
    product: str
    user: str
    count: int

async def create_cart(db, cart: AddToCart, user):
    if not check_product_exists(db, cart.product):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product not found!")
    old_cart= await check_product_exists_in_cart(db, cart.product, user)
    print(old_cart)
    if old_cart is not None:
        await db[collection_name].update_one({'_id': old_cart['_id']},{'$set': {'count': cart.count+ old_cart['count']}})
        return {'success': True}
    cart_to_add= Cart(
        product= cart.product,
        count= cart.count,
        user= user
    )
    encoded = jsonable_encoder(cart_to_add)
    await db[collection_name].insert_one(encoded)
    return {'success': True}

async def check_product_exists_in_cart(db ,product, user):
    cart = await db[collection_name].find_one({"product": product, "user":user})
    return cart

async def get_relevant_cart(db, user):   
    pipeline= get_pipeline(user)
    cart =await db[collection_name].aggregate(pipeline).to_list(5)
    return cart

async def delete_cart(db, id, user):
    check= await db[collection_name].find_one({'_id':id})
    if check is None or check['user']!=user:
        raise HTTPException(status_code=404, detail=f"cart not found")
    cart=await db[collection_name].delete_one({'_id': id})
    if cart.deleted_count == 1:
        return {f"Successfully deleted cart"}
    else:
        raise HTTPException(status_code=404, detail=f"cart not found")

def get_pipeline(user_id):
    return [
        {
  "$match": {
    "user": user_id
  },
        },
  {
    "$lookup": {
      "from": "Products",
      "localField": "product",
      "foreignField": "_id",
      "as": "product_detail"
    }
  },
  
  
]
