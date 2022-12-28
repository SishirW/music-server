from fastapi import APIRouter,HTTPException, Depends, Request,status,UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from server.routers.user import validate_venue
from ..schemas import CreateVenue, ShowUserWithId, ShowVenue, ShowVenueAdmin,Package,Schedule,VenueRating, ShowUser, GetVenueRating,ShowVenueCategory,CreateVenueCategory
from typing import List
from uuid import uuid4
import shutil
from .user import get_current_user

router= APIRouter(prefix= "/venues",tags=["Venues"])

@router.post('/')
async def create_venue(request: Request, venue: CreateVenue,current_user: ShowUserWithId = Depends(validate_venue)):
    venue.id= uuid4()
    venue= jsonable_encoder(venue)
    new_venue= await request.app.mongodb['Venues'].insert_one(venue)
    print('-------------------------',new_venue.inserted_id)
    await request.app.mongodb['Venues'].update_one({'_id': new_venue.inserted_id}, {'$set':{'owner_id':current_user['_id']}})
    return {"success": True, "id":new_venue.inserted_id}

@router.get('/',response_description='Get all venues', response_model=List[ShowVenue])
async def get_venues(request: Request,category: str=None):
    
    if category is None:
        venues=await request.app.mongodb['Venues'].find().to_list(1000)
    else: 
        venues=await request.app.mongodb['Venues'].find({"category":category}).to_list(1000)
        if(len(venues)==0):
            raise HTTPException(status_code=404, detail=f"Venues with category {category} not found")
    
    return venues

# @router.get('/', response_model=List[ShowVenue])
# async def get_venues(request: Request):
#     venues=await request.app.mongodb['Venues'].find().to_list(1000)
#     return venues


@router.get('/my_venue',response_description='Get my venues', response_model=ShowVenueAdmin)
async def get_venue(request: Request,current_user: ShowUser = Depends(validate_venue)):
    venues=await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})
    for data in venues['packages']:
        user_info=[]
        for booking in data['bookings']:
            user=await request.app.mongodb['Users'].find_one({"_id": booking['user_id']})
            if user is not None:
                user_info.append({'complete':booking['complete'],'id':booking['user_id'],'name':user['full_name'],'email':user['email'],'phone_no':user['phone_no']})
        data['bookings']=user_info
    return venues

@router.get('/venue_booking_details',response_description='Get User details who have booked')
async def get_venue_booking_details(request: Request,users:List,current_user: ShowUser = Depends(validate_venue)):
    users2=[]
    for u in users:
        user=await request.app.mongodb['Users'].find_one({"_id": u})
        if user is not None:
            users2.append(user)
    return users2

@router.get('/rate',response_description='View rating of Venue',response_model=List[GetVenueRating])
async def get_venue_rating(request: Request, id:str,current_user: ShowUser = Depends(get_current_user)):
    venue=await request.app.mongodb['Venues'].find_one({"_id": id})
    if venue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    ratings=venue["rating"]
    _ratings=[]
    for rating in ratings:
        user=await request.app.mongodb['Users'].find_one({"_id": rating["user_id"]})
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
async def delete_venue(id: str, request: Request,current_user: ShowUserWithId = Depends(validate_venue)):
    venue=await request.app.mongodb['Venues'].find_one({'_id': id})
    if venue is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {id} not found")
    if venue["owner_id"]!=current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    delete_venue= await request.app.mongodb['Venues'].delete_one({'_id': id})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    # else:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {id} not found")


@router.put('/images/',response_description='Update Venue image')
async def add_venue_images(request: Request, id: str, files: List[UploadFile],current_user: ShowUserWithId = Depends(validate_venue)):
    if files is not None: 
        for file in files:
                image_name= uuid4()
                with open(f"media/venues/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                update_result=await request.app.mongodb['Venues'].update_one({'_id': id}, {'$push':{'images': f'{image_name}.png'}})
                if update_result.matched_count==0: 
                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Venue with id {id} not found')
        return {"Successfully added new images"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')

@router.put('/rate',response_description='Rate Venues')
async def rate_venue(request: Request, rating: VenueRating,current_user: ShowUser = Depends(get_current_user)):
    rating= jsonable_encoder(rating)
    pid=rating['venue_id']
    rating.pop('venue_id')
    rating['user_id']=current_user['_id']
    r=await request.app.mongodb['Venues'].update_one({'_id': pid}, {'$push':{'rating': rating}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'sucess':True}

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

@router.put('/book-package',response_description='Book Venue package')
async def book_package(request: Request,vid: str, pid:str ,current_user: ShowUser = Depends(get_current_user)):
    r=await request.app.mongodb['Venues'].update_one({'_id': vid,'packages._id':{'$eq':pid}},{'$push':{'packages.$.bookings': {'_id':str(uuid4()),'user_id':current_user['_id'],'complete': False}}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'sucess':True}

@router.put('/complete-booked-package',response_description='Complete booked Venue package')
async def complete_booked_package(request: Request,vid: str, pid:str ,bid:str,current_user: ShowUser = Depends(get_current_user)):
    r=await request.app.mongodb['Venues'].update_one({'_id': vid,'packages._id':{'$eq':pid},'packages.bookings._id':{'$eq':bid}},{'$set':{'packages.$.bookings.complete': True}})
    print (r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="venue not found")
    return {'sucess':True}
# @router.put('/packages')
# async def add_packages(request: Request,)
# @router.put('/', response_description='Update Venue', response_model=ShowVenue)
# async def edit_product(id: str, request: Request,product: EditProduct=Depends()):
#     print('-----------------------------------------',product)
#     product= {k: v for k, v in product.dict().items() if v is not None}
    
    
#     if len(product) >= 1:
        
#         update_result = await request.app.mongodb['Products'].update_one(
#             {"_id": id}, {"$set": product}
#         )
        

#         if update_result.modified_count == 1:
#             if (
#                 updated_product := await request.app.mongodb['Products'].find_one({"_id": id})
#             ) is not None:
#                 return updated_product

#     if (
#         existing_product := await request.app.mongodb['Products'].find_one({"_id": id})
#     ) is not None:
#         return existing_product

#     raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
@router.get('/category/',response_description='Get all venues categories', response_model=List[ShowVenueCategory])
async def get_venue_categories(request: Request):
    categories=await request.app.mongodb['VenueCategory'].find().to_list(10000)
    #print(categories)
    return categories

@router.post('/category')
async def create_venue_category(request: Request,category: CreateVenueCategory):
    category.id= uuid4()
    category= jsonable_encoder(category)
    new_category= await request.app.mongodb['VenueCategory'].insert_one(category)
    return {"success": True}

@router.delete('/category/{name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue_category(name: str, request: Request):
    delete_venue= await request.app.mongodb['VenueCategory'].delete_one({'category': name})
    if delete_venue.deleted_count==1:
        return {f"Successfully deleted venue with name {name}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue with name {name} not found")

