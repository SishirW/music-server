from fastapi import APIRouter,HTTPException, Depends, Request,status,UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from server.routers.user import validate_venue
from ..schemas import CreateVenue, ShowUserWithId, ShowVenue, VenueRating, ShowUser, GetVenueRating
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
    return {"Successfully added new venue"}

@router.get('/',response_description='Get all venues', response_model=List[ShowVenue])
async def get_venues(request: Request,category: str=None):
    
    if category is None:
        venues=await request.app.mongodb['Venues'].find().to_list(1000)
    else: 
        venues=await request.app.mongodb['Venues'].find({"category":category}).to_list(1000)
        if(len(venues)==0):
            raise HTTPException(status_code=404, detail=f"Venues with category {category} not found")
    
    return venues

@router.get('/', response_model=List[ShowVenue])
async def get_venues(request: Request):
    venues=await request.app.mongodb['Venues'].find().to_list(1000)
    return venues

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
