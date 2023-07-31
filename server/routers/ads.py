from typing import List
from urllib import response
import uuid
from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from ..schemas import AddToCart, OrderProduct, ShowCart, ShowProduct, ShowProductCart, ShowUser, AddAdvertisment, ShowUserWithId
from .user import validate_admin
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
    if os.path.exists(f"media/advertisments/{image}"):
        os.remove(f"media/advertisments/{image}")
    return {f"Successfully deleted ads with id {id}"}


@router.put('/images/', response_description='Add Advertisment image')
async def add_ad_image(request: Request, file: UploadFile, current_user: ShowUserWithId = Depends(validate_admin)):
    print('aa')
    names = []
    if file is not None:
        image_name = uuid.uuid4()
        with open(f"media/advertisments/{image_name}.png", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        names.append(f"{image_name}.png")
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')
