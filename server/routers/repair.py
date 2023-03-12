from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status, BackgroundTasks
from .user import validate_admin, get_current_user
from ..schemas import RepairForm, ShowUserWithId
from fastapi.encoders import jsonable_encoder
import datetime
import uuid
from typing import List
import shutil
from ..background_tasks import send_notification


router = APIRouter(prefix="/repair", tags=["Repair"])


@router.post('/', response_description="Enquire for repair")
async def create_repair(request: Request, background_tasks: BackgroundTasks, repair: RepairForm, current_user: ShowUserWithId = Depends(get_current_user)):
    print(current_user)
    repair.id = uuid.uuid4()
    repair.date_time = datetime.datetime.now()
    repair = jsonable_encoder(repair)
    new_repair = await request.app.mongodb['Repair'].insert_one(repair)
    await request.app.mongodb['Repair'].update_one({'_id': new_repair.inserted_id}, {'$set': {'owner_id': current_user['_id']}})

    admin = await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)

    devices = []
    for users in admin:
        devices.extend(users['devices'])
    background_tasks.add_task(send_notification, tokens=devices, detail=repair, type='repair',
                              title='Repair', body='New repair request by {}'.format(current_user['full_name']))
    return {"success": True, "id": new_repair.inserted_id}


@router.get('/')
async def get_repair(request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    repair = await request.app.mongodb['Repair'].find().sort("date_time", -1).to_list(10000000)
    return repair


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_repair(id: str, request: Request, current_user: ShowUserWithId = Depends(get_current_user)):
    delete_repair = await request.app.mongodb['Repair'].delete_one({'_id': id})
    if delete_repair.deleted_count == 1:
        return {f"Successfully deleted repair with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"repair with id {id} not found")


@router.put('/images/', response_description='Add Repair Images')
async def add_repair_images(request: Request, files: List[UploadFile], current_user: ShowUserWithId = Depends(get_current_user)):
    names = []
    if files is not None:
        for file in files:
            image_name = uuid.uuid4()
            with open(f"media/repair/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            names.append(f"{image_name}.png")
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')
