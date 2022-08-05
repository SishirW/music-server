from fastapi import APIRouter,HTTPException, Depends, Request,status,UploadFile
from fastapi.encoders import jsonable_encoder
from ..schemas import CreateVenue, ShowVenue
from typing import List
from uuid import uuid4
import shutil

router= APIRouter(prefix= "/venues",tags=["Venues"])

@router.post('/')
async def create_venue(request: Request, files: List[UploadFile],venue: CreateVenue=Depends()):
    venue.id= uuid4()
    venue= jsonable_encoder(venue)
    new_venue= await request.app.mongodb['Venues'].insert_one(venue)
    for file in files:
        image_name= uuid4()
        with open(f"media/venues/{image_name}.png", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        await request.app.mongodb['Venues'].update_one({'_id': new_venue.inserted_id}, {'$push':{'images': f'{image_name}.png'}})
    return {"Successfully added new venue"}

@router.get('/', response_model=List[ShowVenue])
async def get_venues(request: Request):
    venues=await request.app.mongodb['Venues'].find().to_list(1000)
    return venues

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(id: str, request: Request):
    delete_venue= await request.app.mongodb['Venues'].delete_one({'_id': id})
    if delete_venue.deleted_count==1:
        return {f"Successfully deleted venue with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {id} not found")

