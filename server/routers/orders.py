from typing import List
from urllib import response
import uuid
from fastapi import APIRouter,Request,Depends,HTTPException,status
from fastapi.encoders import jsonable_encoder
from ..schemas import AddToCart, OrderProduct, ShowCart, ShowProduct, ShowProductCart, ShowUser
from .user import get_current_user

router= APIRouter(prefix= "/order",tags=["Product orders"])

@router.put('/')
async def place_order(request: Request,orders: List[OrderProduct],current_user: ShowUser = Depends(get_current_user)):
    user= await request.app.mongodb['Users'].find_one({"_id":current_user['_id']})
    for order in orders:
        order.id= uuid.uuid4()
        order.user_id= current_user['_id']
        order= jsonable_encoder(order)
        p= await request.app.mongodb['Products'].find_one({"_id":order['product_id']})
        if p is None:
            raise HTTPException(status_code=404, detail="Product with id {} not found".format(order['product_id']))
        await request.app.mongodb['Orders'].insert_one(order)
        await request.app.mongodb['Products'].update_one({'_id': order['product_id']}, {'$push':{'orders': order['_id']}})
        await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push':{'orders': order['_id']}})

    return {'success':True}

@router.get('/')
async def get_current_orders(request: Request,current_user: ShowUser = Depends(get_current_user)):
    orders=[]
    user= await request.app.mongodb['Users'].find_one({"_id":current_user['_id']})
    
    
    for order_id in user['orders']:
        order= await request.app.mongodb['Orders'].find_one({"_id":order_id})
        if order is None: 
            raise HTTPException(status_code=404, detail="Order with id {} not found".format(order_id))
        if order["status"]=="processing":
            product= await request.app.mongodb['Products'].find_one({"_id":order["product_id"]})
            if product is None: 
                raise HTTPException(status_code=404, detail="Product with id {} not found".format(order["product_id"]))
            
            orders.append({"_id":order["product_id"],
            "name":product["name"],
            "price":product["price"],
            "date": order["date_time"],
            "status":order["status"],
            "type":order["type"] ,
            "image": product["images"][0]})
    return orders


@router.get('/history')
async def get_order_history(request: Request,current_user: ShowUser = Depends(get_current_user)):
    orders=[]
    user= await request.app.mongodb['Users'].find_one({"_id":current_user['_id']})
    
    
    for order_id in user['orders']:
        order= await request.app.mongodb['Orders'].find_one({"_id":order_id})
        if order is None: 
            raise HTTPException(status_code=404, detail="Order with id {} not found".format(order_id))
        if order["status"]=="success" or order["status"]=="canceled":
            product= await request.app.mongodb['Products'].find_one({"_id":order["product_id"]})
            if product is None: 
                raise HTTPException(status_code=404, detail="Product with id {} not found".format(order["product_id"]))
            
            orders.append({"_id":order["product_id"],
            "name":product["name"],
            "price":product["price"],
            "date": order["date_time"],
            "status":order["status"],
            "type":order["type"] ,
            "image": product["images"][0]})
    return orders


    