# from fastapi import APIRouter,HTTPException, Depends, Request,status,UploadFile
# from fastapi.encoders import jsonable_encoder
# from fastapi.responses import Response

# from server.routers.user import validate_venue
# from ..schemas import CreateVenue, ShowUserWithId, EditPackage,ShowVenue, ShowVenueAdmin,Package,Schedule,VenueRating, ShowUser, GetVenueRating,ShowVenueCategory,CreateVenueCategory
# from typing import List
# from uuid import uuid4
# import shutil
# from .user import get_current_user

# router= APIRouter(prefix= "/packages",tags=["Venues"])

# @router.post('/',response_description='Create Venue Package')
# async def create_package(request: Request, package: Package,current_user: ShowUser = Depends(validate_venue)):
#     package.id= uuid4()
#     venue= await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})

#     if venue is None:
#         raise HTTPException(status_code=404, detail=f"Venue not found")
#     package.venue_id=venue['_id']
#     package= jsonable_encoder(package)
#     new_package= await request.app.mongodb['Packages'].insert_one(package)
#     return {"success": True, "id":new_package.inserted_id}

# @router.get('/',response_description='Create Venue Bookings')
# async def get_packages(request: Request,current_user: ShowUser = Depends(validate_venue)):
#     venue= await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})

#     packages=await request.app.mongodb['Packages'].find({"venue_id":venue['_id']}).to_list(1000)
#     return packages

# @router.put('/', response_description='Update Packages')
# async def edit_packages(id: str, package: EditPackage,request: Request,current_user: ShowUser = Depends(validate_venue)):
#     #print('-----------------------------------------',product)
#     package= {k: v for k, v in package.dict().items() if v is not None}
#     venue=await request.app.mongodb['Venues'].find_one({"owner_id":current_user['_id']})

#     if len(package) >= 1:

#         update_result = await request.app.mongodb['Packages'].update_one(
#             {"_id": id, 'venue_id': venue['_id']}, {"$set": package}
#         )


#         if update_result.modified_count == 1:
#             if (
#                 updated_package := await request.app.mongodb['Packages'].find_one({"_id": id})
#             ) is not None:
#                 return updated_package

#     if (
#         existing_package := await request.app.mongodb['Packages'].find_one({"_id": id})
#     ) is not None:
#         return existing_package

#     raise HTTPException(status_code=404, detail=f"package with id {id} not found")

# @router.put('/book-package',response_description='Book Venue package')
# async def book_package(request: Request,vid: str, pid:str ,current_user: ShowUser = Depends(get_current_user)):
#     r=await request.app.mongodb['Packages'].update_one({'_id': pid,'venue_id':vid},{'$push':{'bookings': {'_id':str(uuid4()),'user_id':current_user['_id'],'complete': False}}})
#     print (r.modified_count)
#     if r.modified_count==0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue or package not found")
#     return {'success':True}

# @router.put('/complete-booked-package',response_description='Complete booked Venue package')
# async def complete_booked_package(request: Request,vid: str, pid:str ,bid:str,current_user: ShowUser = Depends(get_current_user)):
#     r=await request.app.mongodb['Packages'].update_one({'_id': pid,'venue_id':vid,'bookings._id':bid},{'$set':{'bookings.$[elem].complete': True}},upsert=False, array_filters=[{"elem._id": bid}],)
#     print (r.modified_count)
#     if r.modified_count==0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
#     return {'success':True}
