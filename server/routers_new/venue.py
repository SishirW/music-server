from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile,BackgroundTasks
from typing import List
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from server.schemas_new.artist import EditSocialMedia
from server.schemas_new.venue import CreateVenueSchema,EditVenueSchema ,CreateReviewSchema, CreatePackageSchema, EditPackageSchema, BookPackageSchema, CreateScheduleSchema, EditScheduleSchema
from ..utils.user import get_current_user, validate_venue, validate_admin
from server.schemas import ShowUserWithId
from server.db import get_database
from server.models.venue import edit_social_media,get_venue_schedule,delete_images, edit_venue,delete_venue,invalid_package,get_venue_package,check_venue_exists,complete_booking,check_seat_available,get_venue_package_booking,get_venue_review,add_review,delete_schedule,edit_schedule,add_schedule,get_requested_venue,verify_venue,unverify_venue, feature_venue,unfeature_venue,add_venue,book_package,edit_package,delete_package,add_package,add_images, get_venue_by_userid, get_venue_byid,get_relevant_venue, get_featured_venue
from ..utils.background_tasks import send_notification

router = APIRouter(prefix="/venue", tags=["Venue"])


@router.post('/')
async def add_new_venue(request: Request, venue: CreateVenueSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_venue(db, venue,current_user['_id'])
    return jsonable_encoder(result)

@router.post('/package')
async def add_new_package(request: Request, package: CreatePackageSchema, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await add_package(db, package, current_user['_id'])
    return jsonable_encoder(result)


@router.post('/booking')
async def book_packages(request: Request,booking: BookPackageSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await book_package(db, current_user['_id'],booking)
    return jsonable_encoder(result)


@router.post('/schedule')
async def add_new_schedule(request: Request, schedule: CreateScheduleSchema, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await add_schedule(db, schedule, current_user['_id'])
    return jsonable_encoder(result)

@router.post('/review')
async def add_new_review(request: Request,review: CreateReviewSchema,background_tasks: BackgroundTasks, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_review(db, review, current_user['_id'])
    print(result)
    user = await request.app.mongodb['Users'].find_one({'_id': result[0]['user_id']})
    if user['devices']!= '' and user['devices']!=None:
        devices = []
        devices.append(user['devices'])   
        background_tasks.add_task(send_notification, tokens=devices, detail=result[0], type='venue_review', title='Your venue has been rated {} by {}'.format(review.rating, current_user['username']), body='Artist has followed you')
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

@router.get('/packages')
async def get_venue_packages(request: Request,page: int = 1, limit: int=20,type:int=0, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await get_venue_package(db,page,limit,type,current_user['_id'])
    return jsonable_encoder(result)

@router.get('/schedule')
async def get_venue_schedules(request: Request,page: int = 1, limit: int=20, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await get_venue_schedule(db,page,limit,current_user['_id'])
    return jsonable_encoder(result)



@router.get('/review')
async def get_venue_reviews(request: Request, id:str,page: int = 1):
    db = get_database(request)
    result = await get_venue_review(db,id,page)
    return jsonable_encoder(result)

@router.get('/booking')
async def get_venue_package_bookings(request: Request, package_id:str,page: int = 1, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await get_venue_package_booking(db,package_id,current_user['_id'],page)
    return jsonable_encoder(result)

@router.get('/packageavailable')
async def check_package_seat_availability(request: Request, package: str, booking_date: datetime, seats: int, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await check_seat_available(db,package, booking_date, seats)
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


@router.put('/', response_description='Edit Venue')
async def edit_venues(request: Request, venue: EditVenueSchema, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await edit_venue(db, venue, current_user['_id'])
    return jsonable_encoder(result)

@router.put('/social', response_description='Update artist social media links')
async def edit_venue_social_media(request: Request, social_links: EditSocialMedia,current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result = await edit_social_media(db, social_links,current_user['_id'])
    return jsonable_encoder(result)

@router.put('/images', response_description='Update venue image')
async def add_venue_images(request: Request, files: List[UploadFile],id: str, type: int=0):
    db = get_database(request)
    venue=await check_venue_exists(db,id)
    result = await add_images(db, id,files,type)
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

@router.put('/invalid', response_description='Make package invalid')
async def invalid_packages(request: Request, package_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await invalid_package(db, package_id, current_user['_id'])
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

@router.put('/complete_booking',response_description='Feature venue')
async def complete_package_booking(request: Request,booking_id: str, current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    result=await complete_booking(db,booking_id, current_user['_id'])
    return jsonable_encoder(result)

@router.delete('/', response_description='Delete venue',status_code=status.HTTP_204_NO_CONTENT)
async def delete_venues(request: Request, id: str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await delete_venue(db, id)
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

@router.delete('/images', response_description='Update product image')
async def delete_venue_images(request: Request, files: List[str],id: str,type: int=0,current_user: ShowUserWithId = Depends(validate_venue)):
    db = get_database(request)
    #artist=await get_artist_by_id(db,id)
    result = await delete_images(db, id,files, type)
    return jsonable_encoder(result)