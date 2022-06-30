from urllib import request
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request,status
from fastapi.encoders import jsonable_encoder
from typing import Union
from datetime import datetime,timedelta
from jose import JWTError, jwt
from ..schemas import CreateUser,ShowUser, TokenData, Token
from ..password_methods import get_password_hash, verify_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router= APIRouter(tags=['User'], prefix='/user')


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "e59412a8495ec43e79483d7010399e5647cb9199ccd4f2f3d0de8b05dd773f92"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.get('/{id}', response_model=ShowUser)
async def get_user(request: Request, id: str):
    user=await request.app.mongodb['Users'].find_one({"_id":id})
    if user is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user



@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: CreateUser):
    user.id= uuid.uuid4()
    user.password= get_password_hash(user.password)
    username= user.username
    user= jsonable_encoder(user)
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


async def get_current_user(request: Request,token: str = Depends(oauth2_scheme)):
    us=''
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

async def authenticate_user(request: Request,username: str, password: str):
    
    user=await request.app.mongodb['Users'].find_one({'username':username})
    if not user:
        return False
    # if not verify_password(password, user.hashed_password):
    #     return False
    return user

# @router.post("/token", response_model=Token)
# async def login_for_access_token(request :Request,form_data: OAuth2PasswordRequestForm = Depends()):
#     #user = authenticate_user(form_data.username, form_data.password)
#     user= await request.app.mongodb['Users'].find_one({'username':form_data.username})
#     print(user)
#     if not user or not verify_password(form_data.password, user['password']):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user['username']}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}