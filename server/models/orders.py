from . import BaseModel
from typing import List
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from server.schemas_new.orders import PlaceOrder
from server.models.products import check_product
from .payment import complete_order_payment
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# from .product_category import check_productcategory_exists
# from server.schemas_new.products import EditProductSchema, CreateReviewSchema, CreateQuestionSchema, CreateQuestionResponseSchema


collection_name= 'Orders'
cart_collection_name= 'Cart'
khalti_url= "https://khalti.com/api/v2/payment/verify/"
class Orders(BaseModel):
    products: List
    user: str
    status: int    # 0 for processing, 1 for confirmed, 2 for cancelled, 3 for completed 
    type: int      # 0 for cash on deilvery. 1 for khalti
    payment: str= None


async def place_order(db, order: PlaceOrder, user):
    products= [x for x in order.products if await check_product(db, x.product)]
    product_ids= []
    for i in products:
        product_ids.append(i.product)
    # print(product_ids)
    if order.type== 1:
        payload = {
        'token': order.payment.khalti_token,
        'amount': order.payment.amount
        }
        headers = {
            'Authorization': 'Key test_secret_key_a290c9bfc87a4c3f9016af3055f3e882'
        }
        
        response = requests.request("POST", khalti_url, headers=headers, data=payload)
        if response.status_code== 200:
            payment_details= await complete_order_payment(db, order.payment, user) 
        else:
            raise HTTPException(status_code=response.status_code, detail= response.text)
        
    ord= Orders(
        user= user,
        status= 0,
        type= order.type,
        payment= payment_details['_id'] if order.type==1 else None,
        products= products,
        )
    encoded = jsonable_encoder(ord)
    new_order= await db[collection_name].insert_one(encoded)
    order_detail= await db[collection_name].find_one(new_order.inserted_id)
    if order.type==1:
        order_detail['idx']= order.payment.idx
    await remove_products_from_user_cart(db, product_ids, user)
    return order_detail

async def remove_products_from_user_cart(db, products, user):
    for product in products:
        info= await db[cart_collection_name].delete_one({"$and": [
        {"product": product},
        {"user": user}
    ]})

        

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

