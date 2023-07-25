from fastapi import APIRouter, Request, Depends,HTTPException,status,BackgroundTasks
from datetime import datetime, timedelta
from ..schemas import Token, TokenData
from ..password_methods import verify_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .user import create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES
from .user import randomDigits
from .user import send_email

router= APIRouter(tags=['Authentication'])


@router.post("/token",response_model=Token)
async def login_for_access_token(request :Request,background_tasks: BackgroundTasks,form_data: OAuth2PasswordRequestForm = Depends()):
    token= request.headers.get('device-token')
    print(token)
    user= await request.app.mongodb['Users'].find_one({'username':form_data.username})
    if user is None:
        user= await request.app.mongodb['Users'].find_one({'email':form_data.username})
    if not user or not verify_password(form_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    validation_number= randomDigits(5)
    created_at= datetime.now()
    if user['verified']==False:
        await request.app.mongodb['Users'].update_one({'username': form_data.username}, {'$push':{'validation_token':{'number':validation_number, 'created_at': created_at}}})
        background_tasks.add_task(send_email,email=user['email'],message=f'Your Confirmation code is {validation_number} .')

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"_id": user['_id'], "detail":"Confirm account to continue"},
        )

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )

    if token!=None:
        await request.app.mongodb['Users'].update_one({'_id': user['_id']}, {'$push':{'devices': token}})
    return {"access_token": access_token, "token_type": "bearer","user_info":user}