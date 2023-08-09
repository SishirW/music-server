from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile
from typing import List
from fastapi.encoders import jsonable_encoder
from server.schemas_new.venue import CreateVenueSchema, CreatePackageSchema, EditPackageSchema, BookPackageSchema
from server.routers.user import validate_user, validate_venue
from server.schemas import ShowUserWithId
from server.db import get_database
from server.models.venue import add_venue,book_package,edit_package,delete_package,add_package,add_images, get_venue_by_userid, get_venue_byid,get_relevant_venue, get_featured_venue

router = APIRouter(prefix="/venue", tags=["Venue"])


@router.post('/')
async def add_new_venue(request: Request, venue: CreateVenueSchema, current_user: ShowUserWithId = Depends(validate_user)):
    db = get_database(request)
    result = await add_venue(db, venue,current_user['_id'])
    return jsonable_encoder(result)

@router.post('/package')
async def add_new_package(request: Request, package: CreatePackageSchema, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await add_package(db, package, current_user['_id'])
    return jsonable_encoder(result)

@router.post('/booking')
async def book_packages(request: Request, package_id: str,booking: BookPackageSchema, current_user: ShowUserWithId = Depends(validate_user)):
    db = get_database(request)
    result = await book_package(db, package_id, current_user['_id'],booking)
    return jsonable_encoder(result)

@router.get('/')
async def get_relevant_venues(request: Request, page: int = 1):
    db = get_database(request)
    result = await get_relevant_venue(db,page)
    return jsonable_encoder(result)


@router.get('/featured')
async def get_featured_venues(request: Request, page: int = 1):
    db = get_database(request)
    result = await get_featured_venue(db,page)
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_venue_by_id(id: str, request: Request):
    db = get_database(request)
    result = await get_venue_byid(db, id)
    return jsonable_encoder(result)

@router.get('/user/{id}')
async def get_venue_by_user_id(id: str, request: Request):
    db = get_database(request)
    result = await get_venue_by_userid(db, id)
    return jsonable_encoder(result)


@router.put('/images', response_description='Update venue image')
async def add_venue_images(request: Request, files: List[UploadFile],id: str):
    db = get_database(request)
    venue=await get_venue_byid(db,id)
    result = await add_images(db, id,files)
    return jsonable_encoder(result)

@router.put('/package', response_description='Update venue package')
async def edit_venue_package(request: Request, package: EditPackageSchema, package_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await edit_package(db,package_id, package, current_user['_id'])
    return jsonable_encoder(result)


@router.delete('/package', response_description='Delete venue package',status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue_package(request: Request, package_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await delete_package(db, package_id, current_user['_id'])
    return jsonable_encoder(result)

