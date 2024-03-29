from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile, BackgroundTasks
from ..utils.user import validate_artist, get_current_user,validate_user_without_error, validate_admin
from fastapi.encoders import jsonable_encoder
from server.schemas_new.artist import EditSocialMedia,CreateArtistSchema, CreateScheduleSchema, EditScheduleSchema, FollowArtistSchema, EditArtistSchema
from server.db import get_database
from server.models.artist import edit_social_media,get_artist_schedule,delete_artist,delete_images,edit_artist,get_artist_info,feature_artist,unfeature_artist,add_artist,get_follower,get_following,get_followers_count,unfollow_artist,follow_artist,edit_schedule,delete_schedule, add_schedule,get_artist_by_userid, Artist, get_artist_byid, get_featured_artist, get_relevant_artist,add_images
from server.schemas import ShowUserWithId
from typing import List
from ..utils.background_tasks import send_notification
from ..models.artist import collection_name

router = APIRouter(prefix="/artist", tags=["Artist"])


@router.post('/')
async def add_new_artist(request: Request, artist: CreateArtistSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_artist(db, artist,current_user['_id'])
    return jsonable_encoder(result)

@router.post('/schedule')
async def add_new_schedule(request: Request, schedule: CreateScheduleSchema, current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    result = await add_schedule(db, schedule, current_user['_id'])
    return jsonable_encoder(result)

@router.post('/follow', response_description='Follow artist')
async def follow_artists(request: Request, follow: FollowArtistSchema, background_tasks: BackgroundTasks,current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result=await follow_artist(db, current_user['_id'], follow)
    if current_user['type']== 'artist':
        user = await request.app.mongodb['Users'].find_one({'_id': result['artist']})
        user_artist= await db[collection_name].find_one({'user_id': result['artist']})
        print(user_artist)
        devices = []
        devices.append(user['devices'])   
        background_tasks.add_task(send_notification, tokens=devices, detail={'id': str(
            user_artist['_id'])}, type='followed-by-artist', title='Followed by artist', body='Artist {} has followed you'.format(user_artist['alias']))
    return jsonable_encoder(result)

@router.get('/')
async def get_relevant_artists(request: Request, page: int = 1, genre: str = None, search: str = None, searchtype: int = 0, current_user: ShowUserWithId = Depends(validate_user_without_error)):
    db = get_database(request)
    result = await get_relevant_artist(db,page, genre, search, searchtype,current_user['_id'])
    return jsonable_encoder(result)

@router.get('/schedule')
async def get_artist_schedules(request: Request,page: int = 1, limit: int=20, current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    result = await get_artist_schedule(db,page,limit,current_user['_id'])
    return jsonable_encoder(result)


@router.get('/featured')
async def get_featured_artists(request: Request, page: int = 1):
    db = get_database(request)
    print('here')
    result = await get_featured_artist(db,page)
    print('Here')
    return jsonable_encoder(result)

@router.get('/followers-count')
async def get_no_of_followers(request: Request, artist: str):
    db = get_database(request)
    result = await get_followers_count(db, artist)
    return jsonable_encoder(result)

@router.get('/followers')
async def get_followers(request: Request, artist: str, current_user: ShowUserWithId = Depends(validate_user_without_error),page: int=1):
    db = get_database(request)
    result = await get_follower(db, artist, page,current_user['_id'])
    return jsonable_encoder(result)

@router.get('/following')
async def get_followings(request: Request, artist: str, current_user: ShowUserWithId = Depends(validate_user_without_error),page: int=1):
    db = get_database(request)
    result = await get_following(db, artist, page,current_user['_id'])
    return jsonable_encoder(result)




@router.get('/{id}')
async def get_artist_by_id(id: str, request: Request, current_user: ShowUserWithId = Depends(validate_user_without_error)):
    db = get_database(request)
    result = await get_artist_byid(db, id, current_user['_id'])
    return jsonable_encoder(result)

@router.get('/user/{id}')
async def get_artist_by_user_id(id: str, request: Request):
    db = get_database(request)
    result = await get_artist_by_userid(db, id)
    return jsonable_encoder(result)

@router.put('/', response_description='Edit Artist')
async def edit_artists(request: Request, artist: EditArtistSchema, current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    result=await edit_artist(db, artist, current_user['_id'])
    return jsonable_encoder(result)

@router.put('/social', response_description='Update artist social media links')
async def edit_artist_social_media(request: Request, social_links: EditSocialMedia,current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    result = await edit_social_media(db, social_links,current_user['_id'])
    return jsonable_encoder(result)

@router.put('/images', response_description='Update artist image')
async def add_artist_images(request: Request, files: List[UploadFile],id: str):
    db = get_database(request)
    artist=await get_artist_info(db,id)
    result = await add_images(db, id,files)
    return jsonable_encoder(result)

@router.put('/schedule', response_description='Update artist schedule')
async def edit_artist_schedule(request: Request, schedule: EditScheduleSchema, schedule_id: str, current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    result=await edit_schedule(db,schedule_id, schedule, current_user['_id'])
    return jsonable_encoder(result)

@router.put('/unfollow', response_description='Follow artist')
async def unfollow_artists(request: Request, follow: FollowArtistSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result=await unfollow_artist(db, current_user['_id'], follow)
    return jsonable_encoder(result)

@router.put('/feature',response_description='Feature artist')
async def feature_artists(request: Request, id:str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await feature_artist(db,id)
    return jsonable_encoder(result)

@router.put('/unfeature',response_description='Feature artist')
async def unfeature_artists(request: Request, id:str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await unfeature_artist(db,id)
    return jsonable_encoder(result)

@router.delete('/', response_description='Delete artist',status_code=status.HTTP_204_NO_CONTENT)
async def delete_artistss(request: Request, id: str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await delete_artist(db, id)
    return jsonable_encoder(result)

@router.delete('/schedule', response_description='Delete artist schedule',status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist_schedule(request: Request, schedule_id: str, current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    result=await delete_schedule(db, schedule_id, current_user['_id'])
    return jsonable_encoder(result)

@router.delete('/images', response_description='Update product image')
async def delete_artist_images(request: Request, files: List[str],id: str,current_user: ShowUserWithId = Depends(validate_artist)):
    db = get_database(request)
    #artist=await get_artist_by_id(db,id)
    result = await delete_images(db, id,files)
    return jsonable_encoder(result)
