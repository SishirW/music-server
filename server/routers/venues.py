from fastapi import APIRouter,HTTPException, Depends, Request,status,UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from server.routers.user import validate_venue
from ..schemas import CreateVenue, ShowUserWithId, CreateFeatured,ShowVenue, ShowVenueAdmin,Package,Schedule,VenueRating, ShowUser, GetVenueRating,ShowVenueCategory,CreateVenueCategory
from typing import List
from uuid import uuid4
import shutil
from .user import get_current_user,validate_admin

router= APIRouter(prefix= "/venues",tags=["Venues"])

@router.post('/')
async def create_venue(request: Request, venue: CreateVenue,current_user: ShowUserWithId = Depends(get_current_user)):
    venue.id= uuid4()
    venue= jsonable_encoder(venue)
    # venue_check=await request.app.mongodb['Venues'].find_one({'owner_id':current_user['_id']})
    # if venue_check is not None:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already has venue")
    new_venue= await request.app.mongodb['Venues'].insert_one(venue)
    await request.app.mongodb['Users'].update_one({'_id': current_user['_id']}, {'$set':{'type': 'venue'}})

    print('-------------------------',new_venue.inserted_id)
    await request.app.mongodb['Venues'].update_one({'_id': new_venue.inserted_id}, {'$set':{'owner_id':current_user['_id'], "validate":True,'avg_rating': 0.0,'no_of_rating':0,'rating':[],'packages': [] }})
    return {"success": True, "id":new_venue.inserted_id}



@router.post('/featured')
async def make_featured_venue(request: Request, venue: CreateFeatured,current_user: ShowUserWithId = Depends(validate_admin)):
    venue.id= uuid4()
    venue= jsonable_encoder(venue)

    venue_check=await request.app.mongodb['Venues'].find_one({"_id":venue['venue_id']})
    if venue_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")

    # venue_check=await request.app.mongodb['Venues'].find_one({'owner_id':current_user['_id']})
    # if venue_check is not None:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already has venue")
    new_venue= await request.app.mongodb['FeaturedVenues'].insert_one(venue)

    print('-------------------------',new_venue.inserted_id)
    return {"success": True, "id":new_venue.inserted_id}

@router.get('/',response_description='Get all venues')
async def get_venues(request: Request,page: int=1,category: str=None,search:str=None,admin:bool=False):
    if page==0:
        page=1
    p=[]
    test={"has_next": False}
    if page is None: 
        page=0
    venues_per_page=10

    if search !=None:
        venues=request.app.mongodb['Venues'].find({"validate":True,"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page-1)*venues_per_page).limit(venues_per_page)
        venue2=request.app.mongodb['Venues'].find({"validate":True,"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page)*venues_per_page).limit(venues_per_page)
        count=0
        async for venue in venues:
            for package in venue['packages']:
                if package["valid"]==False:
                    venue['packages'].remove(package)
            p.append(venue)
        async for venue in venue2:
            count+=1
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        async for venue in venues:
            p.append(venue)
        test['venues']=p
        return test
    if category!=None:
        venues=request.app.mongodb['Venues'].find({"validate":True,"category":category}).skip((page-1)*venues_per_page).limit(venues_per_page)
        venue2=request.app.mongodb['Venues'].find({"validate":True,"category":category}).skip((page)*venues_per_page).limit(venues_per_page)
        count=0
        async for venue in venues:
            for package in venue['packages']:
                if package["valid"]==False:
                    venue['packages'].remove(package)
            p.append(venue)
        async for venue in venue2:
            count+=1
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        
        test['venues']=p
        return test
    if admin:
        venues=request.app.mongodb['Venues'].find({"validate":True}).skip((page-1)*venues_per_page).limit(venues_per_page)
        venue2=request.app.mongodb['Venues'].find({"validate":True}).skip((page)*venues_per_page).limit(venues_per_page)
    else:
        venues=request.app.mongodb['Venues'].find({"validate":True}).sort([('avg_rating',-1),('_id',1)]).skip((page-1)*venues_per_page).limit(venues_per_page)
        venue2=request.app.mongodb['Venues'].find({"validate":True}).sort([('avg_rating',-1),('_id',1)]).skip((page)*venues_per_page).limit(venues_per_page)
    count=0
    async for venue in venues:
       # print(venue)
        for package in venue['packages']:
            if package["valid"]==False:
                venue['packages'].remove(package)
        p.append(venue)
    async for venue in venue2:
        count+=1
    print(count)
    if count==0:
        test['has_next']=False
    else:
        test['has_next']=True
    # async for venue in venues:
    #     p.append(venue)
    test['venues']=p
    return test
    

# @router.get('/', response_model=List[ShowVenue])
# async def get_venues(request: Request):
#     venues=await request.app.mongodb['Venues'].find().to_list(1000)
#     return venues

@router.get('/featured',response_description='Get featured venues')
async def get_featured_venue(request: Request):
    venues=await request.app.mongodb['FeaturedVenues'].find().to_list(10000000)
    for venue1 in venues:
        if venue1['type']=='venue':
            venue=await request.app.mongodb['Venues'].find_one({"_id":venue1['venue_id']})
            for package in venue['packages']:
                if package["valid"]==False:
                    venue['packages'].remove(package)
            venue1['detail']=venue
        else:
            venue=await request.app.mongodb['Venues'].find_one({"_id":venue1['venue_id']})
            for package in venue['packages']:
                if package['_id']==venue1['package_id']:
                    package['venue_name']=venue['name']
                    package['location']=venue['location']
                    venue1['detail']=package
        
    return venues

@router.get('/my_venue',response_description='Get my venues', response_model=ShowVenueAdmin)
async def get_venue(request: Request,current_user: ShowUser = Depends(validate_venue)):
    venues=await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})
    print(venues)
    for data in venues['packages']:
        user_info=[]
        for booking in data['bookings']:
            user=await request.app.mongodb['Users'].find_one({"_id": booking['user_id']})
            if user is not None:
                user_info.append({'complete':booking['complete'],'id':booking['user_id'],'name':user['full_name'],'email':user['email'],'phone_no':user['phone_no']})
        data['bookings']=user_info
    return venues
@router.get('/my_venue_packages_valid',response_description='Get my venues packages')
async def get_venue_packages(request: Request,current_user: ShowUser = Depends(validate_venue)):
    venues=await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})
    if venues is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    datas={'venue_id':venues['_id']}
    packages=[]
    for data in venues['packages']:
        if data['valid']==False:
            continue
        user_info=[]
        for booking in data['bookings']:
            user_info.append({'complete':booking['complete'],'_id':booking['_id'],'name':booking['name'],'email':booking['email'],'phone':booking['phone']})
        data['bookings']=user_info
        packages.append(data)
    datas['packages']=packages
    return datas

@router.get('/my_venue_packages_valid_admin',response_description='Get my venues packages')
async def get_venue_packages_admin(request: Request,id:str,current_user: ShowUser = Depends(validate_admin)):
    venues=await request.app.mongodb['Venues'].find_one({"_id":id})
    if venues is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    packages=[]
    for data in venues['packages']:
        if data['valid']==False:
            continue
        user_info=[]
        for booking in data['bookings']:
            user_info.append({'complete':booking['complete'],'_id':booking['_id'],'name':booking['name'],'email':booking['email'],'phone':booking['phone']})
        data['bookings']=user_info
        packages.append(data)
    return packages

@router.get('/my_venue_packages_invalid',response_description='Get my venues packages')
async def get_venue_packages(request: Request,current_user: ShowUser = Depends(validate_venue)):
    venues=await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})
    if venues is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    datas={'venue_id':venues['_id']}
    packages=[]
    for data in venues['packages']:
        if data['valid']==True:
            continue
        user_info=[]
        for booking in data['bookings']:
            user_info.append({'complete':booking['complete'],'_id':booking['_id'],'name':booking['name'],'email':booking['email'],'phone':booking['phone']})
        data['bookings']=user_info
        packages.append(data)
    datas['packages']=packages
    return datas


@router.get('/my_venue_packages_invalid_admin',response_description='Get my venues packages')
async def get_venue_packages(request: Request,id:str,current_user: ShowUser = Depends(validate_admin)):
    venues=await request.app.mongodb['Venues'].find_one({"_id":id})
    if venues is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    packages=[]
    for data in venues['packages']:
        if data['valid']==True:
            continue
        user_info=[]
        for booking in data['bookings']:
            user_info.append({'complete':booking['complete'],'_id':booking['_id'],'name':booking['name'],'email':booking['email'],'phone':booking['phone']})
        data['bookings']=user_info
        packages.append(data)
    return packages


@router.get('/venue_booking_details',response_description='Get User details who have booked')
async def get_venue_booking_details(request: Request,users:List,current_user: ShowUser = Depends(validate_venue)):
    users2=[]
    for u in users:
        user=await request.app.mongodb['Users'].find_one({"_id": u})
        if user is not None:
            users2.append(user)
    return users2

@router.get('/rate',response_description='View rating of Venue',response_model=List[GetVenueRating])
async def get_venue_rating(request: Request, id:str):
    venue=await request.app.mongodb['Venues'].find_one({"_id": id})
    if venue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    ratings=venue["rating"]
    _ratings=[]
    for rating in ratings:
        user=await request.app.mongodb['Users'].find_one({"_id": rating["user_id"]})
        if user is not None:
            rating["user_image"]="aa"
            rating["user_name"]=user["full_name"]
            rating.pop("user_id")
            _ratings.insert(0,rating)
    return _ratings

# @router.get('/get-package-booking',response_description='Book Venue package')
# async def get_package_booking(request: Request,vid: str, pid:str ,package: Package,current_user: ShowUser = Depends(get_current_user)):
#     package.id=uuid4()
#     package=jsonable_encoder(package)
#     #package["_id"]=uuid4()
#     r=await request.app.mongodb['Venues'].update_one({'_id': vid,'packages._id':{'$eq':pid}},{'$push':{'packages.$.bookings': current_user['_id']}})
#     print (r.modified_count)
#     if r.modified_count==0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
#     return {'sucess':True}

@router.get('/{id}', response_model=ShowVenue)
async def get_venue_by_id(id: str, request: Request):
    
    venue= await request.app.mongodb['Venues'].find_one({"_id":id})
    print('---------------',venue)
    if venue is None:
        raise HTTPException(status_code=404, detail=f"venue with id {id} not found")
    return venue

@router.delete('/',status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(id: str, request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    venue=await request.app.mongodb['Venues'].find_one({'_id': id})
    if venue is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue with id {id} not found")
    owner_id=venue['owner_id']
    delete_venue= await request.app.mongodb['Venues'].delete_one({'_id': id})
    delete_user=await request.app.mongodb['Users'].delete_one({'_id': owner_id})
    if delete_venue.deleted_count==1:
        return {f"Successfully deleted venue with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue with id {id} not found")
@router.delete('/featured',status_code=status.HTTP_204_NO_CONTENT)
async def delete_featured_venue(id: str, request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    venue=await request.app.mongodb['FeaturedVenues'].find_one({'_id': id})
    if venue is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue with id {id} not found")
    delete_venue= await request.app.mongodb['FeaturedVenues'].delete_one({'_id': id})
    if delete_venue.deleted_count==1:
        return {f"Successfully deleted venue with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue with id {id} not found")


@router.put('/images/',response_description='Update Venue image')
async def add_venue_images(request: Request, files: List[UploadFile],current_user: ShowUserWithId = Depends(validate_venue)):
    
    names=[]
    if files is not None: 
        for file in files:
                image_name= uuid4()
                with open(f"media/venues/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                names.append(f"{image_name}.png")
        return {"success":True, "images":names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')

@router.put('/menu-images/',response_description='Update Venue Menu image')
async def add_venue_menu_images(request: Request, files: List[UploadFile],current_user: ShowUserWithId = Depends(validate_venue)):
   
    names=[]
    if files is not None: 
        for file in files:
                image_name= uuid4()
                with open(f"media/venues/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                names.append(f"{image_name}.png")
        return {"success":True, "images":names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')


@router.put('/featured/images/',response_description='Add Featured Venue image')
async def add_featured_venue_images(request: Request, file: UploadFile,current_user: ShowUserWithId = Depends(validate_admin)):
    # venue_check=await request.app.mongodb['FeaturedVenues'].find_one({"_id":id})
    # if venue_check is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    if file is not None: 
        image_name= uuid4()
        with open(f"media/featured_venues/{image_name}.png", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # update_result=await request.app.mongodb['FeaturedVenues'].update_one({'_id': id}, {'$set':{'image': f'{image_name}.png'}})
        # if update_result.matched_count==0: 
        #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Featured Venue with id {id} not found')
        return {"name": f"{image_name}.png"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')

@router.put('/rate',response_description='Rate Venues')
async def rate_venue(request: Request, rating: VenueRating,current_user: ShowUser = Depends(get_current_user)):
    rating= jsonable_encoder(rating)
    pid=rating['venue_id']
    rating.pop('venue_id')
    rating['user_id']=current_user['_id']
    r=await request.app.mongodb['Venues'].update_one({'_id': pid}, {'$push':{'rating': rating}})
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    venue= await request.app.mongodb['Venues'].find_one({"_id":pid})
    ratings=0.0
    count=0
    for rating in venue['rating']:
        ratings=ratings+rating['rating']
        count+=1
    if ratings==0:
        avg=0
    else:
        avg= ratings/count
    print(avg)
    r=await request.app.mongodb['Venues'].update_one({'_id': pid}, {'$set':{'avg_rating': avg,'no_of_rating':count}})
    return {'success':True}

@router.put('/update-schedule',response_description='Update Venue Schedule')
async def update_schedule(request: Request, schedule: Schedule,current_user: ShowUser = Depends(validate_venue)):
    schedule.id=uuid4()
    schedule=jsonable_encoder(schedule)
    #schedule["_id"]=uuid4()
    r=await request.app.mongodb['Venues'].update_one({'owner_id': current_user["_id"]}, {'$push':{'todays_schedule': schedule}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'sucess':True}

@router.put('/update-package',response_description='Update Venue Package')
async def update_package(request: Request, package: Package,current_user: ShowUser = Depends(validate_venue)):
    package.id=uuid4()
    package=jsonable_encoder(package)
    #package["_id"]=uuid4()
    r=await request.app.mongodb['Venues'].update_one({'owner_id': current_user["_id"]}, {'$push':{'packages': package}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'sucess':True}

@router.put('/invalidate-package',response_description='Update Venue Package')
async def invalidate_package(request: Request, pid: str,current_user: ShowUser = Depends(validate_venue)):
    r=await request.app.mongodb['Venues'].update_one({'owner_id': current_user["_id"]}, {'$set':{'packages.$[elem].valid': False}},upsert=False, array_filters=[{"elem._id": pid}])
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {'sucess':True}


@router.put('/delete-package',response_description='Delete Venue Package')
async def delete_package(request: Request, vid: str,pid: str,current_user: ShowUser = Depends(validate_admin)):
    r=await request.app.mongodb['Venues'].update_one({'_id': vid}, {'$pull':{'packages':{'_id':pid}}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {'success':True}

@router.put('/book-package',response_description='Book Venue package')
async def book_package(request: Request,vid: str, pid:str ,current_user: ShowUser = Depends(get_current_user)):
    r=await request.app.mongodb['Venues'].update_one({'_id': vid,'packages._id':{'$eq':pid}},{'$push':{'packages.$.bookings': {'_id':str(uuid4()),'user_id':current_user['_id'],'name':current_user['full_name'],'email':current_user['email'],'phone':current_user['phone_no'],'complete': False}}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'success':True}

@router.put('/complete-booked-package',response_description='Complete booked Venue package')
async def complete_booked_package(request: Request, pid:str ,bid:str,current_user: ShowUserWithId = Depends(validate_venue)):
    print(current_user['_id'])
    r=await request.app.mongodb['Venues'].update_one({'owner_id': current_user["_id"],'packages._id':{'$eq':pid},'packages.bookings._id':{'$eq':bid}},{'$set':{'packages.$[elem].bookings.$[elem2].complete': True}},upsert=False, array_filters=[{"elem._id": pid},{"elem2._id": bid}])
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'success':True}

@router.get('/category/',response_description='Get all venues categories', response_model=List[ShowVenueCategory])
async def get_venue_categories(request: Request):
    categories=await request.app.mongodb['VenueCategory'].find().to_list(10000)
    #print(categories)
    return categories

@router.post('/category')
async def create_venue_category(request: Request,category: CreateVenueCategory,current_user: ShowUserWithId = Depends(validate_admin)):
    category.id= uuid4()
    category= jsonable_encoder(category)
    category['category']=category['category'].lower()
    new_category= await request.app.mongodb['VenueCategory'].insert_one(category)
    return {"success": True}

@router.delete('/category/{name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue_category(name: str, request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    delete_venue= await request.app.mongodb['VenueCategory'].delete_one({'category': name})
    if delete_venue.deleted_count==1:
        return {f"Successfully deleted venue with name {name}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue with name {name} not found")

