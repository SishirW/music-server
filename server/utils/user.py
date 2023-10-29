from urllib import request
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from typing import Union, List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..schemas import  TokenData
from ..utils.password_methods import get_password_hash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import random
import smtplib
from email.mime.text import MIMEText
from ..models import BaseModel
router = APIRouter(tags=['User'], prefix='/user')

class TokenData(BaseModel):
    username: Union[str, None] = None



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




def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



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
    print(user['type'])
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
        return {'_id': None}
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
