from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile
from typing import List
from fastapi.encoders import jsonable_encoder
from server.schemas_new.venue import CreateVenueSchema, CreatePackageSchema, EditPackageSchema, BookPackageSchema, CreateScheduleSchema, EditScheduleSchema
from server.routers.user import validate_user, validate_venue, validate_admin
from server.schemas import ShowUserWithId
from server.db import get_database
from server.models.venue import delete_schedule,edit_schedule,add_schedule,get_requested_venue,verify_venue,unverify_venue, feature_venue,unfeature_venue,add_venue,book_package,edit_package,delete_package,add_package,add_images, get_venue_by_userid, get_venue_byid,get_relevant_venue, get_featured_venue

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


@router.post('/schedule')
async def add_new_schedule(request: Request, schedule: CreateScheduleSchema, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await add_schedule(db, schedule, current_user['_id'])
    return jsonable_encoder(result)


@router.get('/')
async def get_relevant_venues(request: Request, page: int = 1,category: str = None, search: str = None):
    db = get_database(request)
    result = await get_relevant_venue(db,page,category, search)
    return jsonable_encoder(result)


@router.get('/featured')
async def get_featured_venues(request: Request, page: int = 1):
    db = get_database(request)
    result = await get_featured_venue(db,page)
    return jsonable_encoder(result)

@router.get('/request')
async def get_requested_venues(request: Request, page: int = 1, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await get_requested_venue(db,page)
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

@router.put('/schedule', response_description='Update venue schedule')
async def edit_artist_schedule(request: Request, schedule: EditScheduleSchema, schedule_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await edit_schedule(db,schedule_id, schedule, current_user['_id'])
    return jsonable_encoder(result)


@router.put('/feature',response_description='Feature venue')
async def feature_venues(request: Request, id:str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await feature_venue(db,id)
    return jsonable_encoder(result)

@router.put('/unfeature',response_description='Feature venue')
async def unfeature_venues(request: Request, id:str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await unfeature_venue(db,id)
    return jsonable_encoder(result)

@router.put('/verify',response_description='Feature venue')
async def verify_venues(request: Request, id:str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await verify_venue(db,id)
    return jsonable_encoder(result)

@router.put('/unverify',response_description='Feature venue')
async def unverify_venues(request: Request, id:str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await unverify_venue(db,id)
    return jsonable_encoder(result)

@router.delete('/package', response_description='Delete venue package',status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue_package(request: Request, package_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await delete_package(db, package_id, current_user['_id'])
    return jsonable_encoder(result)

@router.delete('/schedule', response_description='Delete artist schedule',status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist_schedule(request: Request, schedule_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await delete_schedule(db, schedule_id, current_user['_id'])
    return jsonable_encoder(result)
