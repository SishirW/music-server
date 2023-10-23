from urllib import request
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from typing import Union, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..schemas import CreateUser, ShowUser, ShowUserType, ShowUserDetailsAdmin, ShowUserWithId, TokenData, Token, EditUserAdditionalDetails, GetAdditionalDetails, ShowUserDetails, ShowUserWithDetails
from ..utils.password_methods import get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import random
import smtplib
from email.mime.text import MIMEText
router = APIRouter(tags=['User'], prefix='/user')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth", auto_error=False)
SECRET_KEY = "e59412a8495ec43e79483d7010399e5647cb9199ccd4f2f3d0de8b05dd773f92"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10000


def randomDigits(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    return random.randint(lower, upper)

# @router.get('/{id}', response_model=ShowUser)
# async def get_user(request: Request, id: str):
#     user=await request.app.mongodb['Users'].find_one({"_id":id})
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
#     return user


async def send_email(email: str, message: str):

    smtp_server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    smtp_server.ehlo()
    smtp_server.starttls()
    smtp_server.login("", "")
    print('--------')
    msg = MIMEText(message)
    msg["Subject"] = "Confirmation Code for account creation"
    msg["To"] = email
    msg["From"] = ""

    smtp_server.send_message(msg)
    return "Email sent successfully!"


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: CreateUser, background_tasks: BackgroundTasks):
    user.id = uuid.uuid4()
    user.password = get_password_hash(user.password)
    username = user.username
    email = user.email
    user = jsonable_encoder(user)
    created_at = datetime.now()
   # user.pop('created_at')
    username_check = await request.app.mongodb['Users'].find_one({"username": username})
    print(username_check)
    if username_check is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=["username", "Username already taken"],
        )
    email_check = await request.app.mongodb['Users'].find_one({"email": email})
    if email_check is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=["email", "Email already taken"],
        )
    new_user = await request.app.mongodb['Users'].insert_one(user)
    await request.app.mongodb['RewardPoints'].insert_one({'_id': str(uuid.uuid4()), 'user': new_user.inserted_id, 'points': 0 })
    validation_number = randomDigits(5)
    await request.app.mongodb['Users'].update_one({'_id': new_user.inserted_id}, {'$set': {'points': 0, 'bookings': [], 'devices': [], 'validation_token': [{'number': validation_number, 'created_at': created_at}]}})
    
    background_tasks.add_task(
        send_email, email=user['email'], message=f'Your Confirmation code is {validation_number} .')

    return {'_id': new_user.inserted_id}


@router.put('/verify')
async def verify_user(request: Request, id: str, token: int):
    user = await request.app.mongodb['Users'].find_one({"_id": id})
    if user == None or user['verified'] == True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot confirm",)
    for codes in user['validation_token']:
        # created_date= datetime.strptime(codes['created_at'], "%Y-%m-%dT%H:%M:%S.%f")
        difference = datetime.now() - codes['created_at']
        difference_in_hour = difference.total_seconds() / 3600

        if codes['number'] == token:
            if difference_in_hour < 2:
                r = await request.app.mongodb['Users'].update_one({'_id': id}, {'$set': {'verified': True}})
                print(r.modified_count)
                access_token_expires = timedelta(
                    days=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": user['username']}, expires_delta=access_token_expires
                )

                if token != None:
                    await request.app.mongodb['Users'].update_one({'_id': user['_id']}, {'$push': {'devices': token}})
                return {"access_token": access_token, "token_type": "bearer", "user_info": user}
            else:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Expired code",)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized",)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# @router.post('/validate', response_model=ShowUserType)
# async def validate(request: Request,token: str= Header(default=None)):
#     credentials_exception = HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user =await request.app.mongodb['Users'].find_one({'username':username})
#     if user is None:
#         raise credentials_exception
#     return user


async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    # print(token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    if user['verified'] == False:
        raise credentials_exception
    return user




async def get_details(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    return user


async def validate_seller(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    print(user)
    if user['type'] != "seller":
        raise credentials_exception
    return user

async def check_is_artist(request: Request, token: str = Depends(optional_oauth2_scheme)):
    if token is None:
        return {'type': 'not_logged_in', 'following': []}
    # print('---------------------- ',token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return {'type': 'not_logged_in'}
        token_data = TokenData(username=username)
    except JWTError:
        return {'type': 'not_logged_in'}
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        return {'type': 'not_logged_in'}
    return {'type': user['type'], 'id': user['_id'], 'following': user['following']}


async def validate_artist(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    if user['type'] != "artist":
        raise credentials_exception
    return user


async def validate_venue(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    if user['type'] != "venue":
        raise credentials_exception
    return user


async def validate_user(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    return user

async def validate_user_without_error(request: Request, token: str = Depends(optional_oauth2_scheme)):
    if token is None:
        return {'_id':None}
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    return user


async def validate_admin(request: Request, token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await request.app.mongodb['Users'].find_one({'username': username})
    if user is None:
        raise credentials_exception
    if user['type'] != "admin":
        raise credentials_exception
    return user


async def authenticate_user(request: Request, username: str, password: str):

    user = await request.app.mongodb['Users'].find_one({'username': username})
    if not user:
        return False
    # if not verify_password(password, user.hashed_password):
    #     return False
    return user


@router.put('/edit_additional_details', response_model=EditUserAdditionalDetails)
async def edit_additional_details(request: Request, detail: EditUserAdditionalDetails, current_user: ShowUser = Depends(get_current_user)):
    detail = {k: v for k, v in detail.dict().items() if v is not None}

    if len(detail) >= 1:

        update_result = await request.app.mongodb['Users'].update_one(
            {"_id": current_user['_id']}, {"$set": detail}
        )

        if update_result.modified_count == 1:
            if (
                updated_detail := await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
            ) is not None:
                return updated_detail

    if (
        existing_detail := await request.app.mongodb['Users'].find_one({"_id": current_user['_id']})
    ) is not None:
        return existing_detail

    raise HTTPException(status_code=404, detail=f"User with id {id} not found")


@router.get('/', response_description='Get all users', response_model=ShowUserDetailsAdmin)
async def get_users(request: Request, page: int = 1, search: str = None, current_user: ShowUserWithId = Depends(validate_admin)):
    if page == 0:
        page = 1
    p = []
    test = {"has_next": False}
    if page is None:
        page = 0
    users_per_page = 3
    if search != None:
        users = request.app.mongodb['Users'].find({"$or": [{"username": {"$regex": f".*{search}.*", '$options': 'i'}}, {
                                                  "email": {"$regex": f".*{search}.*", '$options': 'i'}}]}).skip((page-1)*users_per_page).limit(users_per_page)
        user2 = request.app.mongodb['Users'].find({"$or": [{"username": {"$regex": f".*{search}.*", '$options': 'i'}}, {
                                                  "email": {"$regex": f".*{search}.*", '$options': 'i'}}]}).skip((page)*users_per_page).limit(users_per_page)
        count = 0
        async for user in user2:
            count += 1
        if count == 0:
            test['has_next'] = False
        else:
            test['has_next'] = True
        async for user in users:
            p.append(user)
        test['users'] = p
        return test

    users = request.app.mongodb['Users'].find().skip(
        (page-1)*users_per_page).limit(users_per_page)
    user2 = request.app.mongodb['Users'].find().skip(
        (page)*users_per_page).limit(users_per_page)
    count = 0
    async for user in user2:
        count += 1
    if count == 0:
        test['has_next'] = False
    else:
        test['has_next'] = True
    async for user in users:
        p.append(user)
    test['users'] = p
    return test


@router.get('/get_details', response_model=ShowUserWithDetails)
async def get_user_details(request: Request, current_user: ShowUserWithId = Depends(get_current_user)):
    user = await request.app.mongodb['Users'].find_one({"_id": current_user["_id"]})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    if user['type'] == 'artist':
        artist_check = await request.app.mongodb['Artist'].find_one({'artist_id': current_user['_id']})
        if artist_check is not None:
            user['details'] = artist_check
        else:
            user['details'] = {}
    elif user['type'] == 'venue':
        venue_check = await request.app.mongodb['Venues'].find_one({'owner_id': current_user['_id']})
        if venue_check is not None:
            user['details'] = venue_check
        else:
            user['details'] = {}
    else:
        user['details'] = {}
    return user


@router.get('/get_additional_details', response_model=EditUserAdditionalDetails)
async def get_user_additional_details(request: Request, current_user: ShowUser = Depends(get_current_user)):
    user = await request.app.mongodb['Users'].find_one({"_id": current_user["_id"]})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


@router.get('/get_additional_details_admin', response_model=GetAdditionalDetails)
async def get_user_additional_details(request: Request, id: str, current_user: ShowUser = Depends(validate_admin)):
    user = await request.app.mongodb['Users'].find_one({"_id": id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request, id: str, current_user: ShowUser = Depends(validate_admin)):
    user_check = await request.app.mongodb['Users'].find_one({'_id': id})

    if user_check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    if user_check['_id'] == current_user['_id']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Forbidden")
    type = user_check['type']
    delete_user = await request.app.mongodb['Users'].delete_one({'_id': id})
    if type == 'venue':
        delete_venue = await request.app.mongodb['Venues'].delete_one({'owner_id': id})
    if type == 'artist':
        delete_artist = await request.app.mongodb['Artist'].delete_one({'artist_id': id})
    if delete_user.deleted_count == 1:
        return {f"Successfully deleted user with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {id} not found")


@router.get('/get_bookings_detail')
async def get_bookings_detail(request: Request, current_user: ShowUser = Depends(get_current_user)):
    user = await request.app.mongodb['Users'].find_one({"_id": current_user["_id"]})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user['bookings']


@router.put('/add-device')
async def add_device(request: Request, token: str, current_user: ShowUser = Depends(get_current_user)):
    r = await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push': {'devices': token}})
    if r.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED, detail="Device was not added")
    return {'success': True}


@router.put('/logout')
async def add_device(request: Request, token: str, current_user: ShowUser = Depends(get_current_user)):
    await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$pull': {'devices': token}})
    return {'success': True}


@router.get('/following', response_description='Get artist following')
async def get_following(request: Request, current_user: ShowUserWithId = Depends(check_is_artist)):
    p = []
    user_id = ''
    user_type = ''
    # if(request.headers.__contains__('user_id')):
    #     user_id=request.headers['user_id']
    #     user_type=request.headers['type']

    if current_user['type'] != 'not_logged_in':
        print(current_user['type'])
        if current_user['type'] == 'artist':
            user_id = current_user['id']
            user_type = 'artist'
        else:
            user_id = current_user['id']
            user_type = 'user'
    followings = []

    for following in current_user['following']:
        info = await request.app.mongodb['Artist'].find_one({"_id": following})
        print(info)
        if info is not None:
            info['followers_no'] = len(info['followers'])
            info['following_no'] = len(info['following'])
            if user_id == '':
                info["follows"] = False
            else:
                if user_type == 'artist':
                    artist_info = await request.app.mongodb['Artist'].find_one({'artist_id': user_id})
                    print(artist_info)
                    info["follows"] = False
                    for a in info['followers']:
                        if artist_info['_id'] == a['id']:
                            info["follows"] = True
                            break
                        else:
                            info['follows'] = False
                else:
                    info["follows"] = False
                    for a in info['followers']:
                        if user_id == a['id']:
                            info["follows"] = True
                            break
                        else:
                            info['follows'] = False
            # p.append(artist)

            followings.append(info)

    return followings
