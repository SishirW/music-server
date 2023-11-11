from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile, BackgroundTasks
from typing import List
from fastapi.encoders import jsonable_encoder
from server.db import get_database
from server.schemas_new.used_products import CreateUsedProductSchema, RequestToBuy
from ..utils.user import get_current_user, validate_admin
from server.schemas import ShowUserWithId
from server.models.used_products import get_product_request,request_for_buying,delete_product,get_user_product,get_product_byid,get_product_question,add_product, delete_images,add_images, get_relevant_product, add_question,add_response_to_qn
from server.schemas_new.products import CreateQuestionSchema, CreateQuestionResponseSchema
from ..utils.background_tasks import send_notification

router = APIRouter(prefix="/usedproducts", tags=["Used Products"])



@router.post('/')
async def add_new_product(request: Request, product: CreateUsedProductSchema, background_tasks: BackgroundTasks,current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_product(db, product,current_user['_id'])
    admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

    devices = []
    for users in admin:
        devices.append(users['devices'])
    background_tasks.add_task(send_notification, tokens=devices, detail={}, type='new-used-product',
                              title='Used Product', body='{} has added a new used product:  \nName: {}'.format(current_user['full_name'], result['name']))
    return jsonable_encoder(result)

@router.post('/question')
async def add_new_question(request: Request,question: CreateQuestionSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_question(db, question, current_user['_id'])
    return jsonable_encoder(result)

@router.post('/request')
async def request_to_buy(request: Request,question: RequestToBuy,background_tasks: BackgroundTasks, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await request_for_buying(db, question, current_user['_id'])

    admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

    devices = []
    for users in admin:
        devices.append(users['devices'])
    background_tasks.add_task(send_notification, tokens=devices, detail={'requests': result['request'], 'product': result['products']},
                              type='used-product-request', title='Used Product Request', body='User {} has requested to buy {}'.format(current_user['full_name'], result['products']['name']))
    return jsonable_encoder(result)


@router.get('/')
async def get_relevant_products(request: Request, page: int = 1,category: str = None, search: str = None):
    db = get_database(request)
    result = await get_relevant_product(db,page,category, search)
    return jsonable_encoder(result)

@router.get('/user')
async def get_user_products(request: Request, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await get_user_product(db,current_user['_id'])
    return jsonable_encoder(result)


@router.get('/question')
async def get_product_questions(request: Request, id:str,page: int = 1):
    db = get_database(request)
    result = await get_product_question(db,id,page)
    return jsonable_encoder(result)

@router.get('/request')
async def get_product_requests(request: Request, id:str,page: int = 1, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await get_product_request(db,id,page)
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_product_by_id(id: str, request: Request):
    db = get_database(request)
    result = await get_product_byid(db, id)
    return jsonable_encoder(result)

@router.put('/images', response_description='Update used product image')
async def add_product_images(request: Request, files: List[UploadFile],id: str):
    db = get_database(request)
    result = await add_images(db, id,files)
    return jsonable_encoder(result)

@router.put('/response_to_qn', response_description='Update product question')
async def add_response_to_qns(request: Request, question: CreateQuestionResponseSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result=await add_response_to_qn(db, question, current_user["_id"])
    return jsonable_encoder(result)

@router.delete('/images', response_description='Update product image')
async def delete_product_images(request: Request, files: List[str],id: str,current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await delete_images(db, id,files)
    return jsonable_encoder(result)


@router.delete('/{id}', response_description='Delete product package',status_code=status.HTTP_204_NO_CONTENT)
async def delete_products(request: Request, id:str,current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result=await delete_product(db, id, current_user['_id'], current_user['type'])
    return jsonable_encoder(result)
