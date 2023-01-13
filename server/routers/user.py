from urllib import request
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request,status, Header
from fastapi.encoders import jsonable_encoder
from typing import Union,List
from datetime import datetime,timedelta
from jose import JWTError, jwt
from ..schemas import CreateUser,ShowUser, ShowUserType, ShowUserDetailsAdmin,ShowUserWithId,TokenData, Token,EditUserAdditionalDetails,GetAdditionalDetails,ShowUserDetails
from ..password_methods import get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router= APIRouter(tags=['User'], prefix='/user')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "e59412a8495ec43e79483d7010399e5647cb9199ccd4f2f3d0de8b05dd773f92"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000


# @router.get('/{id}', response_model=ShowUser)
# async def get_user(request: Request, id: str):
#     user=await request.app.mongodb['Users'].find_one({"_id":id})
#     if user is None: 
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
#     return user




@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: CreateUser):
    user.id= uuid.uuid4()
    user.password= get_password_hash(user.password)
    username= user.username
    email=user.email
    user= jsonable_encoder(user)
    username_check= await request.app.mongodb['Users'].find_one({"username":username})
    print(username_check)
    if username_check is not None:
        raise  HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Username already taken",
        )
    email_check= await request.app.mongodb['Users'].find_one({"email":email})
    if email_check is not None:
        raise  HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email already taken",
        )
    new_user= await request.app.mongodb['Users'].insert_one(user)
    return {f'Created a user with username {username}'}




def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post('/validate', response_model=ShowUserType)
async def validate(request: Request,token: str= Header(default=None)):
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    return user


async def get_current_user(request: Request,token: str = Depends(oauth2_scheme)):
    print(token)
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    return user

async def get_details(request: Request,token: str = Depends(oauth2_scheme)):
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    return user


async def validate_seller(request: Request,token: str = Depends(oauth2_scheme)):
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    print(user)
    if user['type']!="seller":
        raise credentials_exception
    return user


async def validate_artist(request: Request,token: str = Depends(oauth2_scheme)):
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    if user['type']!="artist":
        raise credentials_exception
    return user


async def validate_venue(request: Request,token: str = Depends(oauth2_scheme)):
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    if user['type']!="venue":
        raise credentials_exception
    return user

async def validate_admin(request: Request,token: str = Depends(oauth2_scheme)):
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
    user =await request.app.mongodb['Users'].find_one({'username':username})
    if user is None:
        raise credentials_exception
    if user['type']!="admin":
        raise credentials_exception
    return user

async def authenticate_user(request: Request,username: str, password: str):
    
    user=await request.app.mongodb['Users'].find_one({'username':username})
    if not user:
        return False
    # if not verify_password(password, user.hashed_password):
    #     return False
    return user

@router.put('/edit_additional_details',response_model=EditUserAdditionalDetails)
async def edit_additional_details(request: Request, detail: EditUserAdditionalDetails,current_user: ShowUser = Depends(get_current_user)):
    detail= {k: v for k, v in detail.dict().items() if v is not None}
    
    
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


@router.get('/',response_description='Get all users',response_model=ShowUserDetailsAdmin)
async def get_users(request: Request,page: int=1,search:str=None,current_user: ShowUserWithId = Depends(validate_admin)):
    if page==0:
        page=1
    p=[]
    test={"has_next": False}
    if page is None: 
        page=0
    users_per_page=3
    if search!=None:
        users=request.app.mongodb['Users'].find({"$or":[{"username":{"$regex":f".*{search}.*",'$options': 'i'}},{"email":{"$regex":f".*{search}.*",'$options': 'i'}}]}).skip((page-1)*users_per_page).limit(users_per_page)
        user2=request.app.mongodb['Users'].find({"$or":[{"username":{"$regex":f".*{search}.*",'$options': 'i'}},{"email":{"$regex":f".*{search}.*",'$options': 'i'}}]}).skip((page)*users_per_page).limit(users_per_page)
        count=0
        async for user in user2:
            count+=1
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        async for user in users:
            p.append(user)
        test['users']=p
        return test
    

    users=request.app.mongodb['Users'].find().skip((page-1)*users_per_page).limit(users_per_page)
    user2=request.app.mongodb['Users'].find().skip((page)*users_per_page).limit(users_per_page)
    count=0
    async for user in user2:
        count+=1
    if count==0:
        test['has_next']=False
    else:
        test['has_next']=True
    async for user in users:
        p.append(user)
    test['users']=p
    return test
    



@router.get('/get_details', response_model=ShowUserDetails)
async def get_user_details(request: Request,current_user: ShowUser = Depends(get_current_user)):
    user=await request.app.mongodb['Users'].find_one({"_id":current_user["_id"]})
    if user is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.get('/get_additional_details', response_model=EditUserAdditionalDetails)
async def get_user_additional_details(request: Request,current_user: ShowUser = Depends(get_current_user)):
    user=await request.app.mongodb['Users'].find_one({"_id":current_user["_id"]})
    if user is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.get('/get_additional_details_admin', response_model=GetAdditionalDetails)
async def get_user_additional_details(request: Request,id: str,current_user: ShowUser = Depends(validate_admin)):
    user=await request.app.mongodb['Users'].find_one({"_id":id})
    if user is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user

@router.delete('/',status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(request: Request,id: str,current_user: ShowUser = Depends(validate_admin)):
    user_check=await request.app.mongodb['Users'].find_one({'_id':id})
    
    if user_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
    if user_check['_id']==current_user['_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Forbidden")
    type= user_check['type']
    delete_user= await request.app.mongodb['Users'].delete_one({'_id': id})
    if type== 'venue':
        delete_venue= await request.app.mongodb['Venues'].delete_one({'owner_id': id})
    if type== 'artist':
        delete_artist= await request.app.mongodb['Artist'].delete_one({'artist_id': id})
    if delete_user.deleted_count==1:
        return {f"Successfully deleted user with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
