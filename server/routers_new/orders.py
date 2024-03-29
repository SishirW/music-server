from fastapi import Request, HTTPException,APIRouter,Depends,BackgroundTasks
from fastapi import status
from fastapi.encoders import jsonable_encoder
from server.db import get_database
from ..utils.user import  validate_admin, get_current_user
from server.schemas import ShowUserWithId
from server.models.orders import place_order, get_relevant_order, change_order_status, get_user_order
from server.schemas_new.orders import PlaceOrder
from ..utils.background_tasks import send_notification

router = APIRouter(prefix="/order", tags=["Order"])
@router.post('/')
async def order_product(request: Request, order: PlaceOrder,background_tasks: BackgroundTasks, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await place_order(db, order,current_user['_id'])
    admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

    devices = []
    for users in admin:
        devices.append(users['devices'])
    background_tasks.add_task(send_notification, tokens=devices, detail={'id': str(
        result['_id']), 'user_id': current_user['_id']}, type='orders', title='Order', body='New order by {}'.format(current_user['full_name']))
    return jsonable_encoder(result)

@router.get('/')
async def get_relevant_orders(request: Request,status: int=0, page: int = 1, limit: int=5,current_user: ShowUserWithId = Depends(validate_admin)):
    if status> 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    db = get_database(request)
    result = await get_relevant_order(db,status,page, limit)
    return jsonable_encoder(result)

@router.get('/user_orders')
async def get_user_orders(request: Request,type: int=0, page: int = 1, limit: int=20,current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await get_user_order(db,type, page, limit, current_user['_id'])
    return jsonable_encoder(result)


@router.put('/change_status')
async def change_orders_status(request: Request, id: str,type: int, current_user: ShowUserWithId = Depends(validate_admin)):
    if type> 3:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    db = get_database(request)
    result = await change_order_status(db,id, type)
    return jsonable_encoder(result)

