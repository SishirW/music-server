from fastapi import APIRouter, Request, Depends,HTTPException,status
from datetime import datetime, timedelta
from ..schemas import Token, TokenData
from ..password_methods import verify_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .user import create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES
from .user import randomDigits

router= APIRouter(tags=['Authentication'])


@router.post("/token",response_model=Token)
async def login_for_access_token(request :Request,form_data: OAuth2PasswordRequestForm = Depends()):
    user= await request.app.mongodb['Users'].find_one({'username':form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    validation_number= randomDigits(5)
    created_at= datetime.now()
    if user['verified']==False:
        await request.app.mongodb['Users'].update_one({'username': form_data.username}, {'$push':{'validation_token':{'number':validation_number, 'created_at': str(created_at)}}})
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"_id": user['_id'], "detail":"Confirm account to continue"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer","user_info":user}