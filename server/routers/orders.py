from typing import List
from urllib import response
import uuid
from fastapi import APIRouter, Request, Depends, HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from ..schemas import AddToCart, OrderProduct, ShowCart, ShowProduct, ShowProductCart, ShowUser
from .user import get_current_user, validate_admin
import requests
from ..utils.background_tasks import send_notification

router = APIRouter(prefix="/order", tags=["Product orders"])


@router.post('/')
async def place_order(request: Request, background_tasks: BackgroundTasks, orders: OrderProduct, current_user: ShowUser = Depends(get_current_user)):
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
    order_id = uuid.uuid4()
    orders.id = order_id
    orders.user_id = current_user['_id']
    orders = jsonable_encoder(orders)
    for order in orders['product_ids']:
        p = await request.app.mongodb['Products'].find_one({"_id": order['id']})
        if p is None:
            raise HTTPException(
                status_code=404, detail="Product with id {} not found".format(order['id']))

    await request.app.mongodb['Orders'].insert_one(orders)
    for order in orders['product_ids']:
        print(order)
        await request.app.mongodb['Products'].update_one({'_id': order['id']}, {'$push': {'orders': orders['_id']}})
    await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push': {'orders': orders['_id']}})
    for product in orders["product_ids"]:
        await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$pull': {'cart': {"product_id": {"$eq": product["id"]}}}})

    admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

    devices = []
    for users in admin:
        devices.extend(users['devices'])
    background_tasks.add_task(send_notification, tokens=devices, detail={'id': str(
        order_id), 'user_id': current_user['_id']}, type='orders', title='Order', body='New order by {}'.format(current_user['full_name']))

    return {'success': True}


@router.post('/khalti')
async def place_order_khalti(request: Request, background_tasks: BackgroundTasks, orders: OrderProduct, current_user: ShowUser = Depends(get_current_user)):
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
    order_id = uuid.uuid4()
    orders.id = order_id
    orders.user_id = current_user['_id']
    orders = jsonable_encoder(orders)
    print(orders)
    payload = {
        'token': orders['khalti_details']['token'],
        'amount': orders['khalti_details']['price']
    }
    headers = {
        'Authorization': 'Key test_secret_key_a290c9bfc87a4c3f9016af3055f3e882'
    }
    url = "https://khalti.com/api/v2/payment/verify/"
    response = requests.request("POST", url, headers=headers, data=payload)
    if (response.status_code == 200):

        for order in orders['product_ids']:
            p = await request.app.mongodb['Products'].find_one({"_id": order['id']})
            if p is None:
                raise HTTPException(
                    status_code=404, detail="Product with id {} not found".format(order['id']))

        await request.app.mongodb['Orders'].insert_one(orders)
        for order in orders['product_ids']:
            print(order)
            await request.app.mongodb['Products'].update_one({'_id': order['id']}, {'$push': {'orders': orders['_id']}})
        await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push': {'orders': orders['_id']}})
        for product in orders["product_ids"]:
            await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$pull': {'cart': {"product_id": {"$eq": product["id"]}}}})
        admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

        devices = []
        for users in admin:
            devices.extend(users['devices'])
        background_tasks.add_task(send_notification, tokens=devices, detail={'id': str(
            order_id), 'user_id': current_user['_id']}, type='orders', title='Order', body='New order by {}'.format(current_user['full_name']))

        return {'success': True}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No transaction found")


@router.get('/')
async def get_current_orders(request: Request, current_user: ShowUser = Depends(get_current_user)):
    orders = []
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})

    for order_id in user['orders']:
        order = await request.app.mongodb['Orders'].find_one({"_id": order_id})
        if order is not None and order["status"] == "processing":
            for p in order["product_ids"]:
                product = await request.app.mongodb['Products'].find_one({"_id": p["id"]})
                if product is not None:
                    orders.append({"_id": order["_id"],
                                   "name": product["name"],
                                   "price": product["price"],
                                   "date": order["date_time"],
                                   "status": order["status"],
                                   "type": order["type"],
                                   "image": product["images"][0]})
    orders.reverse()
    return orders


@router.get('/history')
async def get_order_history(request: Request, current_user: ShowUser = Depends(get_current_user)):
    orders = []
    user = await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
    for order_id in user['orders']:
        order = await request.app.mongodb['Orders'].find_one({"_id": order_id})
        if order is not None and order["status"] == "complete" or order["status"] == "cancelled":
            for p in order["product_ids"]:
                product = await request.app.mongodb['Products'].find_one({"_id": p["id"]})
                if product is not None:
                    orders.append({"_id": order["_id"],
                                   "name": product["name"],
                                   "price": product["price"],
                                   "date": order["date_time"],
                                   "status": order["status"],
                                   "type": order["type"],
                                   "image": product["images"][0]})
    orders.reverse()
    return orders


@router.get('/processing')
async def get_processing_orders(request: Request, page: int = 1, current_user: ShowUser = Depends(validate_admin)):
    orders_per_page = 3
    orders_list = []
    orders_detail = {}
    orders = request.app.mongodb['Orders'].find({'status': 'processing'}).sort(
        'date_time', -1).skip((page-1)*orders_per_page).limit(orders_per_page)
    orders2 = request.app.mongodb['Orders'].find({'status': 'processing'}).sort(
        'date_time', -1).skip((page)*orders_per_page).limit(orders_per_page)
    async for order in orders:
        user = await request.app.mongodb['Users'].find_one({"_id": order['user_id']})
        if user is not None:
            order['user_name'] = user['full_name']
        else:
            order['user_name'] = 'Deleted User'
        orders_list.append(order)

    count = 0
    async for order in orders2:
        count += 1
    if count == 0:
        orders_detail['has_next'] = False
    else:
        orders_detail['has_next'] = True
    orders_detail['orders'] = orders_list
    return orders_detail


@router.get('/cancelled')
async def get_cancelled_orders(request: Request, page: int = 1, current_user: ShowUser = Depends(validate_admin)):
    orders_per_page = 3
    orders_list = []
    orders_detail = {}
    orders = request.app.mongodb['Orders'].find({'status': 'cancelled'}).skip(
        (page-1)*orders_per_page).limit(orders_per_page)
    orders2 = request.app.mongodb['Orders'].find({'status': 'cancelled'}).skip(
        (page)*orders_per_page).limit(orders_per_page)
    print(orders)
    async for order in orders:
        user = await request.app.mongodb['Users'].find_one({"_id": order['user_id']})
        if user is not None:
            order['user_name'] = user['full_name']
        else:
            order['user_name'] = 'Deleted User'
        orders_list.append(order)

    count = 0
    async for order in orders2:
        count += 1
    if count == 0:
        orders_detail['has_next'] = False
    else:
        orders_detail['has_next'] = True
    orders_detail['orders'] = orders_list
    return orders_detail


@router.get('/complete')
async def get_completed_orders(request: Request, page: int = 1, current_user: ShowUser = Depends(validate_admin)):
    orders_per_page = 3
    orders_list = []
    orders_detail = {}
    orders = request.app.mongodb['Orders'].find({'status': 'complete'}).skip(
        (page-1)*orders_per_page).limit(orders_per_page)
    orders2 = request.app.mongodb['Orders'].find({'status': 'complete'}).skip(
        (page)*orders_per_page).limit(orders_per_page)
    print(orders)
    async for order in orders:
        user = await request.app.mongodb['Users'].find_one({"_id": order['user_id']})
        if user is not None:
            order['user_name'] = user['full_name']
        else:
            order['user_name'] = 'Deleted User'
        orders_list.append(order)

    count = 0
    async for order in orders2:
        count += 1
    if count == 0:
        orders_detail['has_next'] = False
    else:
        orders_detail['has_next'] = True
    orders_detail['orders'] = orders_list
    return orders_detail


@router.get('/processing_detail')
async def get_orders_detail(request: Request, id: str, current_user: ShowUser = Depends(validate_admin)):
    order = await request.app.mongodb['Orders'].find_one({"_id": id})
    if order is None:
        raise HTTPException(
            status_code=404, detail=f"Order with id {id} not found")
    for o in order["product_ids"]:
        product = await request.app.mongodb['Products'].find_one({"_id": o['id']})
        if product is not None:
            o["name"] = product["name"]
        else:
            o["name"] = "Deleted Product"
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


@router.put('/complete_order', response_description='Complete product Order')
async def complete_order(request: Request, background_tasks: BackgroundTasks, id: str, type: int = 0, current_user: ShowUser = Depends(validate_admin)):
    if type == 0:
        r = await request.app.mongodb['Orders'].update_one({'_id': id}, {'$set': {'status': 'complete'}})
        order = await request.app.mongodb['Orders'].find_one({'_id': id})
        user = await request.app.mongodb['Users'].find_one({'_id': order['user_id']})
        if user is not None:
            user_point = user['points']
            total_points = 0
            for product in order['product_ids']:
                temp_product = await request.app.mongodb['Products'].find_one({'_id': product['id']})
                if temp_product is not None:
                    total_points += temp_product['points']*product['quantity']
            await request.app.mongodb['Users'].update_one({'_id': order['user_id']}, {'$set': {'points': user_point+total_points}})
    else:
        r = await request.app.mongodb['Orders'].update_one({'_id': id}, {'$set': {'status': 'cancelled'}})
        order = await request.app.mongodb['Orders'].find_one({'_id': id})
        user = await request.app.mongodb['Users'].find_one({'_id': order['user_id']})
        devices = user['devices']
        background_tasks.add_task(send_notification, tokens=devices, detail={
        }, type='order-cancelled', title='Order Cancelled', body='Your recent order has been cancelled.')

    print(r.modified_count)
    if r.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return {'success': True}
