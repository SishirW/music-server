from fastapi import Request, HTTPException,APIRouter,status
from fastapi.encoders import jsonable_encoder
from server.schemas_new.user import CreateUserSchema, EditUserSchema
from server.models.user import verify_user,create_user, find_user_by_id, find_user_by_email, find_user_by_username,delete_user_by_id,edit_user_details
from server.db import get_database
router = APIRouter(prefix="/user", tags=["User"])


@router.post('/')
async def create_new_user(request: Request, user: CreateUserSchema):
    db = get_database(request)
    result = await create_user(db, user)
    return jsonable_encoder(result)

@router.get('/{id}', response_model=CreateUserSchema)
async def get_user_by_id(id: str, request: Request):
    db = get_database(request)
    result = await find_user_by_id(db, id)
    return jsonable_encoder(result)

@router.get('/email/{id}', response_model=CreateUserSchema)
async def get_user_by_email(email: str, request: Request):
    db = get_database(request)
    result = await find_user_by_email(db, email)
    return jsonable_encoder(result)

@router.get('/username/{id}', response_model=CreateUserSchema)
async def get_user_by_username(username: str, request: Request):
    db = get_database(request)
    result = await find_user_by_username(db, username)
    return jsonable_encoder(result)

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_by_id(id: str, request: Request):
    db = get_database(request)
    result = await delete_user_by_id(db, id)
    return jsonable_encoder(result)

@router.put('/verify')
async def verify_users(request: Request, id: str, token: int):
    db = get_database(request)
    result = await verify_user(db, id, token)
    return jsonable_encoder(result)
@router.put('/{id}')
async def edit_user_by_id(id: str, request: Request,info: EditUserSchema):
    db = get_database(request)
    result = await edit_user_details(db, id,info)
    return jsonable_encoder(result)