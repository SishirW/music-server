from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile
from server.routers.user import validate_user
from fastapi.encoders import jsonable_encoder
from server.schemas_new.artist import CreateArtistSchema
from server.db import get_database
from server.models.artist import add_artist, get_artist_by_userid, Artist, get_artist_byid, get_featured_artist, get_relevant_artist,add_images
from server.schemas import ShowUserWithId
from typing import List
router = APIRouter(prefix="/artist", tags=["Artist"])


@router.post('/')
async def add_new_artist(request: Request, artist: CreateArtistSchema, current_user: ShowUserWithId = Depends(validate_user)):
    db = get_database(request)
    result = await add_artist(db, artist,current_user['_id'])
    return jsonable_encoder(result)

@router.get('/')
async def get_relevant_artists(request: Request, page: int = 1):
    db = get_database(request)
    result = await get_relevant_artist(db,page)
    return jsonable_encoder(result)


@router.get('/featured')
async def get_featured_artists(request: Request, page: int = 1):
    db = get_database(request)
    print('here')
    result = await get_featured_artist(db,page)
    print('Here')
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_artist_by_id(id: str, request: Request):
    db = get_database(request)
    result = await get_artist_byid(db, id)
    return jsonable_encoder(result)

@router.get('/user/{id}')
async def get_artist_by_user_id(id: str, request: Request):
    db = get_database(request)
    result = await get_artist_by_userid(db, id)
    return jsonable_encoder(result)

@router.put('/images', response_description='Update artist image')
async def add_artist_images(request: Request, files: List[UploadFile],id: str):
    db = get_database(request)
    artist=await get_artist_byid(db,id)
    result = await add_images(db, id,files)
    return jsonable_encoder(result)