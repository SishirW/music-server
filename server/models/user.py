from . import BaseModel, PydanticBaseModel, PyObjectId
from typing import List, Optional
from pydantic import EmailStr, Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status, BackgroundTasks
from ..utils.password_methods import get_password_hash
from ..utils.user import randomDigits, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, timedelta
from ..utils.background_tasks import send_email


collection_name = "Users"
verification_collection_name = "VerificationToken"
rewardcollection_name = "RewardPoints"
follow_collection_name = 'ArtistFollow'


class VerificationToken(BaseModel):
    token: int
    user: str
    valid: bool = True


class UserType(BaseModel):
    typeName: str


class SocialMedia(BaseModel):
    facebook: Optional[str] = ''
    instagram: Optional[str] = ''
    tiktok: Optional[str] = ''
    youtube: Optional[str] = ''
    twitter: Optional[str] = ''


class RewardPoints(BaseModel):
    user: str
    points: int


class User(BaseModel):
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    verified: bool = False
    type: str= 'user'
    location: Optional[str] 
    phone_no: Optional[str] 
    devices: List[str]= []
    points: int =0
    type: str = 'user'
    location: Optional[str] = ''
    phone_no: Optional[str] = ''
    devices: List[str] = []
    points: int = 0
    social_links: Optional[SocialMedia]


async def create_user(db, user):
    old_user = await db[collection_name].find_one({"email": user.email})
    if old_user is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={'message': f"User with email {user.email} already exists!", "type": "email"})
    old_user = await db[collection_name].find_one({"username": user.username})
    if old_user is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={'message': f"User with username {user.username} already exists!", "type": "username"})

    user1 = User(
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
        phone_no=user.phone_no,
    )
    encoded = jsonable_encoder(user1)
    print(encoded)
    user_entry = await db[collection_name].insert_one(encoded)
    verification_number = randomDigits(5)
    await add_verification_token(db, user_entry.inserted_id, verification_number)
    await add_reward_points(db, user_entry.inserted_id)
    # new_user = await find_band_by_id(db, str(bnd.id), user)
    # return new_band

    return {'_id': user_entry.inserted_id, 'email': user.email, 'verification_number': verification_number}


async def add_verification_token(db, user, token):
    user1 = VerificationToken(
        token=token,
        user=user
    )
    encoded = jsonable_encoder(user1)
    print(encoded)
    await db[verification_collection_name].insert_one(encoded)
    return True


async def add_reward_points(db, user):
    user1 = RewardPoints(
        user=user,
        points=0
    )
    encoded = jsonable_encoder(user1)
    print(encoded)
    await db[rewardcollection_name].insert_one(encoded)
    return True


async def verify_user(db, user, token):
    user_check = await find_user_by_id(db, user)
    if user_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'user not found!')
    if user_check['verified'] == True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot verify',)
    token_detail = await db[verification_collection_name].find_one({'token': token, 'user': user})
    if token_detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'token not found!')
    difference_in_hour = calculate_difference_in_hour(
        datetime.strptime(token_detail['created_at'], '%Y-%m-%dT%H:%M:%S.%f'))

    if token== token_detail['token'] and token_detail['valid']:
        # if difference_in_hour < 2: 
        r = await db[collection_name].update_one({'_id': user}, {'$set': {'verified': True}})
        return get_login_token_after_verification(user_check)
    if token == token_detail['token'] and token_detail['valid']:
        if difference_in_hour < 24*600:
            r = await db[collection_name].update_one({'_id': user}, {'$set': {'verified': True}})
            return get_login_token_after_verification(user_check)
        await db[verification_collection_name].update_one({'_id': token_detail['_id']}, {'$set': {'valid': 'False'}})
    raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Expired code",)


def get_login_token_after_verification(user):
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "user_info": user}


def calculate_difference_in_hour(time):
    difference = datetime.now() - time
    difference_in_hour = difference.total_seconds() / 3600
    return difference_in_hour


async def find_user_by_id(db, id):
    user = await db[collection_name].find_one({"_id": id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    return user


async def get_user_detail(db, id):
    user = await db[collection_name].find_one({"_id": id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    pipeline = get_detail_pipeline(id, user['type'])
    detail = await db[collection_name].aggregate(pipeline).to_list(12)
    return detail


async def find_user_by_email(db, email):
    user = await db[collection_name].find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    return user


async def find_user_by_username(db, username):
    user = await db[collection_name].find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user not found!")
    return user


async def delete_user_by_id(db, id):
    user = await db[collection_name].delete_one({'_id': id})
    if user.deleted_count != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found")

async def delete_logged_in_user(db, id, type):
    if type!= 'admin':
        await db[collection_name].delete_one({'_id': id})
    if type=='artist':
        artist=await db['Artist'].delete_one({'user_id': id}) 
    if type=='venue':
        artist=await db['Venue'].delete_one({'user_id': id})   
    



async def edit_user_details(db, id, user_info):
    user_info = {k: v for k, v in user_info.dict().items() if v is not None}

    if len(user_info) >= 1:

        update_result = await db[collection_name].update_one(
            {"_id": id}, {"$set": user_info}
        )

        if update_result.modified_count == 1:
            if (
                updated_user_info := await db[collection_name].find_one({"_id": id})
            ) is not None:
                return updated_user_info

    if (
        existing_user_info := await db[collection_name].find_one({"_id": id})
    ) is not None:
        return existing_user_info

    raise HTTPException(status_code=404, detail=f"User with id {id} not found")


async def get_following(db, page, user_id):

    pipeline = [
        {
            "$match": {
                "user": user_id
            }
        },
        {
            "$lookup": {
                "from": "Artist",
                "localField": "artist",
                "foreignField": "user_id",
                "as": "artist_detail"
            }
        },
        {
            "$lookup": {
                "from": "ArtistFollow",
                "localField": "artist",
                "foreignField": "artist",
                "as": "artist_followers"
            }
        },
        {
            "$addFields": {
                "isFollowedByUser": {
                    "$in": [
                        user_id,
                        "$artist_followers.user"
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "artist_detail": "$artist_detail",
                "following": "$isFollowedByUser"
            }
        },
        {
            "$skip": (page-1)*5
        },
        {
            "$limit": 5
        }
    ]
    following = await db[follow_collection_name].aggregate(pipeline).to_list(5)
    return following


def get_detail_pipeline(user, type):
    if (type == 'artist'):
        return [
            {
                "$match": {
                    "_id": user
                }
            },
            {
                "$unset": ["password", "devices"]
            },
            {
                "$lookup": {
                    "from": "RewardPoints",
                    "localField": "_id",
                    "foreignField": "user",
                    "as": "points_detail"
                }
            },
            {
                "$lookup": {
                    "from": "Artist",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "artist_details"
                }
            },
            {
                "$lookup": {
                    "from": "SocialMedia",
                    "localField": "artist_details.social_accounts",
                    "foreignField": "_id",
                    "as": "social_media"
                }
            },
            {
                "$lookup": {
                    "from": "ArtistFollow",
                    "localField": "_id",
                    "foreignField": "artist",
                    "as": "artist_followers"
                }
            },
            {
                "$lookup": {
                    "from": "ArtistFollow",
                    "localField": "_id",
                    "foreignField": "user",
                    "as": "artist_following"
                }
            },
            {
                "$addFields": {

                    "followers_count": {
                        "$size": "$artist_followers"
                    },
                    "following_count": {
                        "$size": "$artist_following"
                    }
                }
            },
            {
                "$unset": ["artist_followers", "artist_following"]
            },

        ]
    elif (type == 'venue'):
        return [
            {
                "$match": {
                    "_id": user
                }
            },
            {
                "$unset": ["password", "devices"]
            },
            {
                "$lookup": {
                    "from": "RewardPoints",
                    "localField": "_id",
                    "foreignField": "user",
                    "as": "points_detail"
                }
            },
            {
                "$lookup": {
                    "from": "Venue",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "venue_details"
                }
            },
            {
                "$lookup": {
                    "from": "SocialMedia",
                    "localField": "venue_details.social_accounts",
                    "foreignField": "_id",
                    "as": "social_media"
                }
            },
            {
                "$lookup": {
                    "from": "ArtistFollow",
                    "localField": "_id",
                    "foreignField": "user",
                    "as": "artist_following"
                }
            },
            {
                "$addFields": {

                    "following_count": {
                        "$size": "$artist_following"
                    }
                }
            },
            {
                "$unset": ["artist_following"]
            },
        ]

    else:
        return [
            {
                "$match": {
                    "_id": user
                }

            },
            {
                "$lookup": {
                    "from": "RewardPoints",
                    "localField": "_id",
                    "foreignField": "user",
                    "as": "points_detail"
                }
            },
            {
                "$lookup": {
                    "from": "ArtistFollow",
                    "localField": "_id",
                    "foreignField": "user",
                    "as": "artist_following"
                }
            },
            {
                "$addFields": {

                    "following_count": {
                        "$size": "$artist_following"
                    }
                }
            },
            {
                "$unset": ["password", "devices", "artist_following"]
            },

        ]
