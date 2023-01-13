from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status
from .user import validate_admin,get_current_user
from ..schemas import GrowForm,ShowUserWithId
from fastapi.encoders import jsonable_encoder
import uuid


router= APIRouter(prefix= "/grow",tags=["Grow"])

@router.post('/',response_description="Enquire for grow")
async def create_grow(request: Request,grow: GrowForm,current_user: ShowUserWithId = Depends(get_current_user)):
    print(current_user)
    grow.id= uuid.uuid4()
    grow= jsonable_encoder(grow)
    new_grow= await request.app.mongodb['Grow'].insert_one(grow)
    await request.app.mongodb['Grow'].update_one({'_id': new_grow.inserted_id}, {'$set':{'owner_id':current_user['_id']}})
    return {"success": True, "id":new_grow.inserted_id}

@router.get('/')
async def get_grow(request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    grow= await request.app.mongodb['Grow'].find().to_list(10000000)
    return grow

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_grow(id: str, request: Request,current_user: ShowUserWithId = Depends(get_current_user)):
    delete_grow= await request.app.mongodb['Grow'].delete_one({'_id': id})
    if delete_grow.deleted_count==1:
        return {f"Successfully deleted grow with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grow with id {id} not found")