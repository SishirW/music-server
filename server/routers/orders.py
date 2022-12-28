from typing import List
from urllib import response
import uuid
from fastapi import APIRouter,Request,Depends,HTTPException,status
from fastapi.encoders import jsonable_encoder
from ..schemas import AddToCart, OrderProduct, ShowCart, ShowProduct, ShowProductCart, ShowUser
from .user import get_current_user,validate_admin

router= APIRouter(prefix= "/order",tags=["Product orders"])

@router.post('/')
async def place_order(request: Request,orders: OrderProduct,current_user: ShowUser = Depends(get_current_user)):
    user= await request.app.mongodb['Users'].find_one({"_id":current_user['_id']})
    orders.id= uuid.uuid4()
    orders.user_id= current_user['_id']
    orders= jsonable_encoder(orders)
    for order in orders['product_ids']: 
        p= await request.app.mongodb['Products'].find_one({"_id":order['id']})
        if p is None:
            raise HTTPException(status_code=404, detail="Product with id {} not found".format(order['id']))
    
    await request.app.mongodb['Orders'].insert_one(orders)
    for order in orders['product_ids']:
        print(order) 
        await request.app.mongodb['Products'].update_one({'_id': order['id']}, {'$push':{'orders': orders['_id']}})
    await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push':{'orders': orders['_id']}})
    for product in orders["product_ids"]:
        await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$pull':{'cart': {"product_id":{"$eq":product["id"]}}}})
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
            for p in order["product_ids"]:
                product= await request.app.mongodb['Products'].find_one({"_id":p["id"]})
                if product is not None:   
                    orders.append({"_id":order["_id"],
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


@router.get('/processing')
async def get_processing_orders(request: Request,current_user: ShowUser = Depends(validate_admin)):
    
    order= await request.app.mongodb['Orders'].find().sort('date_time', 1).to_list(1000)
    
    return order

@router.get('/processing_detail')
async def get_processing_orders_detail(request: Request,id: str,current_user: ShowUser = Depends(validate_admin)):
    order= await request.app.mongodb['Orders'].find_one({"_id":id})
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    for o in order["product_ids"]:
        product=await request.app.mongodb['Products'].find_one({"_id":o['id']})
        if product is not None:
            o["name"]=product["name"]
        else:
            o["name"]="Deleted Product"
    # for o in order["product_ids"]:
    #     dict1={}
    #     product=await request.app.mongodb['Products'].find_one({"_id":o['id']})
    #     if product is not None:
    #         dict1['name']=product['name']
    #         dict1['type']=order['type']
    #         dict1['quantity']=o['quantity']
    #         dict1['time']=order['date_time']
    #         dict1['order_id']=order['_id']
    #         detail.append(dict1)
    # return detail
    return order
