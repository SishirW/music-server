from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status
from ..schemas import CreateArtist, ShowUserWithId, ShowArtist, CreateArtistCategory,ShowArtistCategory
import uuid
from typing import List
from .user import get_current_user, validate_artist,validate_admin
import shutil
from fastapi.encoders import jsonable_encoder
router= APIRouter(prefix= "/artist",tags=["Artist"])
from jose import JWTError, jwt

@router.post('/',response_description="Add new artist")
async def create_artist(request: Request,artist: CreateArtist,current_user: ShowUserWithId = Depends(get_current_user)):
    print(current_user)
    artist.id= uuid.uuid4()
    artist= jsonable_encoder(artist)
    # artist_check=await request.app.mongodb['Artist'].find_one({'artist_id':current_user['_id']})
    # if artist_check is not None:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already has artist")
    # artist_check= await request.app.mongodb['Artist'].find_one({"artist_id":current_user['_id']})
    # print(artist_check)
    # if artist_check is not None:
    #     raise  HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Forbidden",
    #     )
    await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$set':{'type': 'artist'}})
    new_artist= await request.app.mongodb['Artist'].insert_one(artist)
    #await request.app.mongodb['artists'].update(  {  $set : {"address":1} }  )
    await request.app.mongodb['Artist'].update_one({'_id': new_artist.inserted_id}, {'$set':{'artist_id':current_user['_id'],'rating':[],'followers_count':0}})
    # for file in files:
    #     image_name= uuid4()
    #     with open(f"media/artists/{image_name}.png", "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
        
    #     await request.app.mongodb['artists'].update_one({'_id': new_artist.inserted_id}, {'$push':{'images': f'{image_name}.png'}})
    return {"success": True, "id":new_artist.inserted_id}

@router.get('/',response_description='Get all artist')
async def get_artist(request: Request,page: int=1,category: str=None,search:str=None,admin: bool=False):
    if page==0:
        page=1
    p=[]
    user_id=''
    test={"has_next": False}
    user_type=''
    if page is None: 
        page=1
    artists_per_page=11
    if(request.headers.__contains__('user_id')):
        user_id=request.headers['user_id']
        user_type=request.headers['type']

    if search !=None:
        artists=request.app.mongodb['Artist'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page-1)*artists_per_page).limit(artists_per_page)
        artist2=request.app.mongodb['Artist'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page)*artists_per_page).limit(artists_per_page)
        count=0
        async for artist in artists:
            artist['followers_no']=len(artist['followers'])
            artist['following_no']=len(artist['following'])
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
            p.append(artist)
        
        async for artist in artist2:
            count+=1
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        async for artist in artists:
            p.append(artist)
        test['artists']=p
        return test
    
    if category !=None:
        artists=request.app.mongodb['Artist'].find({"category":category}).skip((page-1)*artists_per_page).limit(artists_per_page)
        artist2=request.app.mongodb['Artist'].find({"category":category}).skip((page)*artists_per_page).limit(artists_per_page)
        count=0
        async for artist in artists:
            artist['followers_no']=len(artist['followers'])
            artist['following_no']=len(artist['following'])
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
            p.append(artist)
        async for artist in artist2:
            count+=1
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        
        test['artists']=p
        return test
    if admin:
        artists=request.app.mongodb['Artist'].find().skip((page-1)*artists_per_page).limit(artists_per_page)
        artist2=request.app.mongodb['Artist'].find().skip((page)*artists_per_page).limit(artists_per_page)
    else:
        artists=request.app.mongodb['Artist'].find().sort([('featured',-1),('followers_count',-1),('_id',1)]).skip((page-1)*artists_per_page).limit(artists_per_page)
        artist2=request.app.mongodb['Artist'].find().sort([('featured',-1),('followers_count',-1),('_id',1)]).skip((page)*artists_per_page).limit(artists_per_page)
    count=0
    async for artist in artists:
            artist['followers_no']=len(artist['followers'])
            artist['following_no']=len(artist['following'])
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
            p.append(artist)
    async for artist in artist2:
        print(artist)
        count+=1
    if count==0:
        test['has_next']=False
    else:
        test['has_next']=True
    
    test['artists']=p
    return test


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
    p=[]
    user_id=''
    user_type=''
    if(request.headers.__contains__('user_id')):
        user_id=request.headers['user_id']
        user_type=request.headers['type']
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
                info['followers_no']=len(info['followers'])
                info['following_no']=len(info['following'])
                if user_id=='':
                    info["follows"]=False
                else:
                    if user_type=='artist':
                        artist_info= await request.app.mongodb['Artist'].find_one({'artist_id': user_id})
                        info["follows"]=False
                        for a in info['followers']: 
                            if artist_info['_id'] == a['id']:
                                info["follows"]=True
                                break
                            else:
                                info['follows']=False 
                    else:
                        info["follows"]=False
                        for a in info['followers']: 
                            if user_id == a['id']:
                                info["follows"]=True
                                break
                            else:
                                info['follows']=False 
                # p.append(artist)
                
                followings.append(info)

    
    return followings


@router.put('/images/',response_description='Update Product image')
async def add_artist_images(request: Request, files: List[UploadFile]):
    names=[]
    if files is not None: 
        for file in files:
                image_name= uuid.uuid4()
                with open(f"media/artist/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                names.append(f"{image_name}.png")
        return {"success":True, "images":names}
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
    
    art= await request.app.mongodb['Artist'].find_one({"_id":id})
    artist_no_of_followers=art['followers_count']
    
    r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$set':{'followers_count': artist_no_of_followers+1}})
    return {'success':True}

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


@router.put('/feature',response_description="Feature/Unfeature Artist")
async def feature_artist(request: Request,id: str,feature:bool,current_user: ShowUserWithId = Depends(validate_admin)):
    artist_info= await request.app.mongodb['Artist'].find_one({'_id': id})
    if artist_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artist not found")
    if feature:
        r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$set':{'featured': True}})
    else:
        r=await request.app.mongodb['Artist'].update_one({'_id': id}, {'$set':{'featured': False}})
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Cannot change featured")
    return {'success':True}



@router.get('/category/',response_description='Get all Artist categories', response_model=List[ShowArtistCategory])
async def get_artist_categories(request: Request):
    categories=await request.app.mongodb['ArtistCategory'].find().to_list(1000)
    #print(categories)
    return categories

@router.post('/category')
async def create_artist_category(request: Request,category: CreateArtistCategory, current_user: ShowUserWithId = Depends(validate_admin)):
    category.id= uuid.uuid4()
    category= jsonable_encoder(category)
    category['category']=category['category'].lower()
    new_category= await request.app.mongodb['ArtistCategory'].insert_one(category)
    return {"success": True}

@router.delete('/category/{name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist_category(name: str, request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    delete_product= await request.app.mongodb['ArtistCategory'].delete_one({'category': name})
    if delete_product.deleted_count==1:
        return {f"Successfully deleted product with name {name}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with name {name} not found")

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_artist(id: str, request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    artist_check=await request.app.mongodb['Artist'].find_one({'_id':id})
    if artist_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artist not found")
    owner_id=artist_check['artist_id']
    delete_artist= await request.app.mongodb['Artist'].delete_one({'_id': id})
    delete_user=await request.app.mongodb['Users'].delete_one({'_id': owner_id})
    if delete_artist.deleted_count==1:
        return {f"Successfully deleted artist with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artist with id {id} not found")

