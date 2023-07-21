from fastapi import APIRouter, Request, Depends, HTTPException, status
from server.schemas import ShowUser
from server.routers.user import validate_admin, validate_user
from server.schemas_new.genres import AddGenreSchema
from server.models.genres import add_new_genre, delete_genre_by_id, find_all_genres, find_genre_by_id, get_total_genre_count
from fastapi.encoders import jsonable_encoder


from server.db import get_database

router = APIRouter(prefix="/genres", tags=["Genres"])


@router.get('/')
async def get_genres(request: Request, page=1, limit=5, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await find_all_genres(db, int(page), int(limit))
    return jsonable_encoder(result)


@router.get('/count')
async def get_total_genres_count(request: Request, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await get_total_genre_count(db)
    return jsonable_encoder(result)


@router.get('/{id}')
async def get_genre_by_id(id: str, request: Request, current_user: ShowUser = Depends(validate_user)):
    db = get_database(request)
    result = await find_genre_by_id(db, id)
    return jsonable_encoder(result)


@router.post('/')
async def add_genre(request: Request, genre: AddGenreSchema, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    print("result", end='\n'*7)
    result = await add_new_genre(db, genre)
    print(dir(result), end='\n'*7)
    print("result", end='\n'*7)
    return jsonable_encoder(result)


@router.delete('/{id}')
async def delete_genre(id: str, request: Request, current_user: ShowUser = Depends(validate_admin)):
    db = get_database(request)
    result = await delete_genre_by_id(db, id)
    return jsonable_encoder(result)


# @router.put('/{id}')
# async def delete_genre(id: str, request: Request, genre, current_user: ShowUser = Depends(validate_admin)):
#     db = get_database(request)
#     result = await delete_genre_by_id(db, id)
#     return jsonable_encoder(result)
