from fastapi import Request, HTTPException,APIRouter,status,Depends, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from server.schemas_new.user import CreateUserSchema, EditUserSchema, UserDetail
from server.models.user import get_following,get_user_detail,verify_user,create_user, find_user_by_id, find_user_by_email, find_user_by_username,delete_user_by_id,edit_user_details
from server.db import get_database
from server.schemas import ShowUserWithId
from ..utils.user import  validate_admin, get_current_user
from ..utils.background_tasks import send_email

router = APIRouter(prefix="/user", tags=["User"])


@router.post('/')
async def create_new_user(request: Request,background_tasks: BackgroundTasks, user: CreateUserSchema):
    db = get_database(request)
    result = await create_user(db, user)
    background_tasks.add_task(
        send_email, email=user.email, message=f"Your Confirmation code is {result['verification_number']} .")
    return {'_id': result['_id']}

@router.get('/detail',)
async def get_user_details(request: Request, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await get_user_detail(db, current_user['_id'])
    return jsonable_encoder(result)

@router.get('/following')
async def get_followings(request: Request, current_user: ShowUserWithId = Depends(get_current_user),page: int=1):
    db = get_database(request)
    result = await get_following(db, page,current_user['_id'])
    return jsonable_encoder(result)


@router.get('/{id}', response_model=CreateUserSchema)
async def get_user_by_id(id: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await find_user_by_id(db, id)
    return jsonable_encoder(result)

@router.get('/email/{id}', response_model=CreateUserSchema)
async def get_user_by_email(email: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await find_user_by_email(db, email)
    return jsonable_encoder(result)

@router.get('/username/{id}', response_model=CreateUserSchema)
async def get_user_by_username(username: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await find_user_by_username(db, username)
    return jsonable_encoder(result)

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_by_id(id: str, request: Request, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await delete_user_by_id(db, id)
    return jsonable_encoder(result)

@router.put('/verify')
async def verify_users(request: Request, id: str, token: int):
    db = get_database(request)
    result = await verify_user(db, id, token)
    return jsonable_encoder(result)

@router.put('/logout')
async def logout(request: Request, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    await db['Users'].update_one({'_id': current_user['_id']}, {'$set': {'devices': ''}})
    return {'success': True}

@router.put('/detail')
async def edit_user_detail(request: Request,info: EditUserSchema,current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await edit_user_details(db, current_user['_id'],info)
    return jsonable_encoder(result)

@router.put('/{id}')
async def edit_user_by_id(id: str, request: Request,info: EditUserSchema, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await edit_user_details(db, id,info)
    return jsonable_encoder(result)