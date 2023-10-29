from typing import List
from urllib import response
import uuid
from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from ..schemas import AddToCart, OrderProduct, ShowCart, ShowProduct, ShowProductCart, ShowUser, AddAdvertisment, ShowUserWithId
from ..utils.user import validate_admin
import shutil
import os

router = APIRouter(prefix="/ads", tags=["Advertisment"])


@router.post('/', response_description="Add Advertisment")
async def add_ads(request: Request, ads: AddAdvertisment, current_user: ShowUserWithId = Depends(validate_admin)):
    print(current_user)
    ads.id = uuid.uuid4()
    ads = jsonable_encoder(ads)
    new_ads = await request.app.mongodb['Advertisment'].insert_one(ads)
    return {"success": True, "id": new_ads.inserted_id}


@router.get('/')
async def get_advertisment(request: Request):
    grow = await request.app.mongodb['Advertisment'].find().to_list(10000000)
    return grow


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_ads(id: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    ads = await request.app.mongodb['Advertisment'].find_one({"_id": id})
    if ads is None:
        raise HTTPException(
            status_code=404, detail=f"ads with id {id} not found")
    image = ads['image']
    delete_ads = await request.app.mongodb['Advertisment'].delete_one({'_id': id})
    return {f"Successfully deleted ads with id {id}"}


@router.put('/images', response_description='Add Advertisment image')
async def add_ad_image(request: Request,id: str, file: UploadFile, current_user: ShowUserWithId = Depends(validate_admin)):
    

    ads = await request.app.mongodb['Advertisment'].find_one({"_id": id})
    if ads is None:
        raise HTTPException(
            status_code=404, detail=f"ads with id {id} not found")
    name = ''

    if file is not None:
        image_name = uuid.uuid4()
        os.makedirs(f'media_new/advertisments', exist_ok=True)
        with open(f"media_new/advertisments/{image_name}.png", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        name= f"{image_name}.png"
        await request.app.mongodb['Advertisment'].update_one({'_id': id}, {'$set': {'image':name }})
        return {"success": True, "images": name}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')
