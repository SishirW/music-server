from . import BaseModel
from typing import List
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from server.schemas_new.orders import PlaceOrder
from server.models.products import check_product
from .payment import complete_order_payment

# from .product_category import check_productcategory_exists
# from server.schemas_new.products import EditProductSchema, CreateReviewSchema, CreateQuestionSchema, CreateQuestionResponseSchema


collection_name= 'Orders'

class Orders(BaseModel):
    products: List
    user: str
    status: int    # 0 for processing, 1 for confirmed, 2 for cancelled, 3 for completed 
    type: int      # 0 for cash on deilvery. 1 for khalti
    payment: str= None


async def place_order(db, order: PlaceOrder, user):
    products= [x for x in order.products if await check_product(db, x.product)]
    if order.type== 1:
        payment_details= await complete_order_payment(db, order.payment, user)
    ord= Orders(
        user= user,
        status= 0,
        type= order.type,
        payment= payment_details['_id'] if order.type==1 else None,
        products= products,
        )
    encoded = jsonable_encoder(ord)
    new_order= await db[collection_name].insert_one(encoded)
    return {'success': True}

async def get_relevant_order(db,status ,page, limit):
    pipeline= get_pipeline(page,limit, status)
    order =await db[collection_name].aggregate(pipeline).to_list(5)
    return order


async def change_order_status(db, id,type):
    await db[collection_name].update_one({'_id':id}, {'$set':{'status': type}})
    return {'success':True}





def get_pipeline(page, limit, type):
    return [
            {
    "$match": {
        "status":  type,
    },
            },
  {
    "$lookup": {
      "from": "Products",
      "localField": "products.product",
      "foreignField": "_id",
      "as": "product_detail"
    }
  },
  
  {
    "$skip": (page-1)*5
  },
  {
    "$limit": limit
  }
]

