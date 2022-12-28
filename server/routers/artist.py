from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status
from ..schemas import CreateArtist, ShowUserWithId, ShowArtist, ShowUser,TokenData
import uuid
from typing import List
from .user import get_current_user, validate_artist
import shutil
from fastapi.encoders import jsonable_encoder
router= APIRouter(prefix= "/artist",tags=["Artist"])
from jose import JWTError, jwt
from .user import SECRET_KEY,ALGORITHM,get_details

@router.post('/',response_description="Add new artist")
async def create_artist(request: Request,artist: CreateArtist,current_user: ShowUserWithId = Depends(validate_artist)):
    print(current_user)
    artist.id= uuid.uuid4()
    artist= jsonable_encoder(artist)
    # artist_check= await request.app.mongodb['Artist'].find_one({"artist_id":current_user['_id']})
    # print(artist_check)
    # if artist_check is not None:
    #     raise  HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Forbidden",
    #     )
    new_artist= await request.app.mongodb['Artist'].insert_one(artist)
    #await request.app.mongodb['artists'].update(  {  $set : {"address":1} }  )
    await request.app.mongodb['Artist'].update_one({'_id': new_artist.inserted_id}, {'$set':{'images': [],'artist_id':current_user['_id'],'rating':[]}})
    # for file in files:
    #     image_name= uuid4()
    #     with open(f"media/artists/{image_name}.png", "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
        
    #     await request.app.mongodb['artists'].update_one({'_id': new_artist.inserted_id}, {'$push':{'images': f'{image_name}.png'}})
    return {"success": True, "id":new_artist.inserted_id}

@router.get('/',response_description='Get all artist', response_model=List[ShowArtist])
async def get_artist(request: Request,page: int=0,category: str=None):
    p=[]
    user_id=''
    user_type=''
    if page is None: 
        page=0
    artists_per_page=2
    if(request.headers.__contains__('user_id')):
        user_id=request.headers['user_id']
        user_type=request.headers['type']
    if category is None:
        artists=request.app.mongodb['Artist'].find().skip(page*artists_per_page).limit(artists_per_page)
        async for artist in artists:
            if user_id=='':
                artist["follows"]=False
            else:
                if user_type=='artist':
                    artist_info= await request.app.mongodb['Artist'].find_one({'artist_id': user_id})
                    artist["follows"]=False
                    for a in artist['followers']: 
                        if artist_info['_id'] == a['id']:
                            artist["follows"]=True
                            break
                        else:
                            artist['follows']=False 
                else:
                    artist["follows"]=False
                    for a in artist['followers']: 
                        if user_id == a['id']:
                            artist["follows"]=True
                            break
                        else:
                            artist['follows']=False 
            print(artist)
            p.append(artist)
        # if user_id=='':
        #     for artist in p:
        #         artist["follows"]=False
        # for artist in p:
        #     if user_id in artist['followers']:
        #         artist['follows']=True
        #     else:
        #         artist['follows']=False
    else: 
        artists=await request.app.mongodb['Artist'].find({"category":category}).to_list(1000)
        if(len(artists)==0):
            raise HTTPException(status_code=404, detail=f"artists with category {category} not found")
    
    return p

@router.get('/followers',response_description='Get artist followers')
async def get_artist_followers(request: Request,id: str,page: int,category: str=None):
    followers=[]
    if category is None:
        products=await request.app.mongodb['Artist'].find().to_list(1000)
    if id is None: 
        raise HTTPException(status_code=404, detail=f"Id is missing")
    else: 
        artist=await request.app.mongodb['Artist'].find_one({"_id":id})
        for follower in artist['followers']:
            info= await request.app.mongodb['Artist'].find_one({"_id":follower})
            print(info)
            followers.append({'_id': follower,'name': info['name'],'image': 'image'})

        if(len(products)==0):
            raise HTTPException(status_code=404, detail=f"Products with category {category} not found")
    
    return followers

@router.get('/following',response_description='Get artist following', response_model=List[ShowArtist])
async def get_artist_following(request: Request,id: str):
    followings=[]
    if id is None: 
        raise HTTPException(status_code=404, detail=f"Id is missing")
    else: 
        artist=await request.app.mongodb['Artist'].find_one({"_id":id})
        if artist is None:
            raise HTTPException(status_code=404, detail=f"Artist with id {id} not found")
        for following in artist['following']:
            info= await request.app.mongodb['Artist'].find_one({"_id":following})
            print(info)
            if info is not None:
                followings.append(info)
                #followings.append({'_id': following,'name': info['name'],'images': info['images'],'location': info['location'],'description': info['description'],'skills': info['images']})
    
    return followings


@router.put('/images/{id}',response_description='Update Product image')
async def add_artist_images(request: Request, id: str, files: List[UploadFile]):
    if files is not None: 
        for file in files:
                image_name= uuid.uuid4()
                with open(f"media/artist/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                update_result=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$push':{'images': f'{image_name}.png'}})
                if update_result.matched_count==0: 
                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'artist with id {id} not found')
        return {"Successfully added new images"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')

@router.put('/follow',response_description="Follow Artist")
async def follow_artist(request: Request,id: str,current_user: ShowUserWithId = Depends(get_current_user)):
    if(current_user["type"]=="artist"):
        artist_info= await request.app.mongodb['Artist'].find_one({'artist_id': current_user['_id']})
        r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$push':{'followers': {"id":artist_info['_id'],"type":"artist"}}})
        if r.modified_count==0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
        
        await request.app.mongodb['Artist'].update_one({'_id': artist_info['_id']}, {'$push':{'following': id}})
    else:
        r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$push':{'followers': {"id":current_user['_id'],"type":"user"}}})
        if r.modified_count==0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
        await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$push':{'following': id}})
    return {"success": True}

@router.put('/unfollow',response_description="Unfollow Artist")
async def unfollow_artist(request: Request,id: str,current_user: ShowUserWithId = Depends(get_current_user)):
    if(current_user["type"]=="artist"):
        artist_info= await request.app.mongodb['Artist'].find_one({'artist_id': current_user['_id']})
        r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$pull':{'followers': {"id":artist_info['_id'],"type":"artist"}}})
        if r.modified_count==0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
        artist_info= await request.app.mongodb['Artist'].find_one({'artist_id': current_user['_id']})
        await request.app.mongodb['Artist'].update_one({'_id': artist_info['_id']}, {'$pull':{'following': id}})
    else:
        r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$pull':{'followers': {"id":current_user['_id'],"type":"user"}}})
        if r.modified_count==0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
        await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$pull':{'following': id}})
    return {"success": True}