from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status, BackgroundTasks
from .user import validate_admin, get_current_user
from ..schemas import GrowForm, ShowUserWithId, GrowVideoForm
from fastapi.encoders import jsonable_encoder
import uuid
from ..background_tasks import send_notification
from datetime import datetime


router = APIRouter(prefix="/grow", tags=["Grow"])


@router.post('/', response_description="Enquire for grow")
async def create_grow(request: Request, grow: GrowForm, background_tasks: BackgroundTasks, current_user: ShowUserWithId = Depends(get_current_user)):
    # print(current_user)
    grow.id = uuid.uuid4()
    grow = jsonable_encoder(grow)
    new_grow = await request.app.mongodb['Grow'].insert_one(grow)
    await request.app.mongodb['Grow'].update_one({'_id': new_grow.inserted_id}, {'$set': {'owner_id': current_user['_id'], 'date_added': datetime.now()}})
    admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

    # devices = []
    # for users in admin:
    #     devices.extend(users['devices'])
    # background_tasks.add_task(send_notification, tokens=devices, detail={
    # }, type='grow', title='Grow', body='New enquiry at {} by {}'.format(grow['type'], grow['name']))

    return {"success": True, "id": new_grow.inserted_id}


@router.post('/video', response_description="Add grow video")
async def create_grow_video(request: Request, grow: GrowVideoForm, current_user: ShowUserWithId = Depends(validate_admin)):
    print(current_user)
    grow.id = uuid.uuid4()
    grow = jsonable_encoder(grow)
    new_grow = await request.app.mongodb['GrowVideo'].insert_one(grow)
    return {"success": True, "id": new_grow.inserted_id}


@router.get('/')
async def get_grow(request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    grow = await request.app.mongodb['Grow'].find().sort('date_added', -1).to_list(10000000)
    return grow


@router.get('/video')
async def get_grow_video(request: Request):
    grow = await request.app.mongodb['GrowVideo'].find().to_list(10000000)
    return grow


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_grow(id: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    delete_grow = await request.app.mongodb['Grow'].delete_one({'_id': id})
    if delete_grow.deleted_count == 1:
        return {f"Successfully deleted grow with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Grow with id {id} not found")


@router.delete('/video', status_code=status.HTTP_204_NO_CONTENT)
async def delete_grow_video(id: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    delete_grow = await request.app.mongodb['GrowVideo'].delete_one({'_id': id})
    if delete_grow.deleted_count == 1:
        return {f"Successfully deleted grow with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Grow with id {id} not found")


# @router.get('/test')
# async def test(request: Request, background_tasks: BackgroundTasks):
#     data = await request.app.mongodb['Grow'].find_one({'_id': '67ace4c8-1c05-47f9-9225-11ce8ea55f34'})
#     background_tasks.add_task(send_notification, data)
#     return {'success'}
