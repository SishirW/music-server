import uuid
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Request, Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List,Set, Union 
from ..schemas import CreateProduct, EditProduct, ShowProduct, ShowUser
from .user import get_current_user
import shutil
from uuid import uuid1, uuid4


router= APIRouter(prefix= "/products",tags=["Musical products"])


@router.post('/',response_description="Add new product")
async def create_product(request: Request, files: List[UploadFile],product: CreateProduct= Depends(),current_user: ShowUser = Depends(get_current_user)):
    product.id= uuid.uuid4()
    product= jsonable_encoder(product)
    
    new_product= await request.app.mongodb['Products'].insert_one(product)
    for file in files:
        image_name= uuid4()
        with open(f"media/{image_name}.png", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        await request.app.mongodb['Products'].update_one({'_id': new_product.inserted_id}, {'$push':{'images': f'{image_name}.png'}})
    return {"success": True}


@router.get('/',response_description='Get all products', response_model=List[ShowProduct])
async def get_products(request: Request,current_user: ShowUser = Depends(get_current_user)):
    products=await request.app.mongodb['Products'].find().to_list(1000)
    return products

@router.get('/{id}', response_model=ShowProduct)
async def get_product_by_id(id: str, request: Request):
    
    product= await request.app.mongodb['Products'].find_one({"_id":id})
    print('---------------',product)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    return product

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: str, request: Request):
    delete_product= await request.app.mongodb['Products'].delete_one({'_id': id})
    if delete_product.deleted_count==1:
        return {f"Successfully deleted product with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {id} not found")




@router.put('/{id}', response_description='Update Product', response_model=ShowProduct)
async def edit_product(id: str, request: Request,file: Union[UploadFile, None] = None,product: EditProduct=Depends()):
    product= {k: v for k, v in product.dict().items() if v is not None}
    print('-------------',file)
    if len(product) >= 1:
        
        update_result = await request.app.mongodb['Products'].update_one(
            {"_id": id}, {"$set": product}
        )
        if file is not None:
            image_name= uuid4()
            with open(f"media/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            update_result=await request.app.mongodb['Products'].update_one({'_id': id}, {'$push':{'images': f'{image_name}.png'}})

        if update_result.modified_count == 1:
            if (
                updated_product := await request.app.mongodb['Products'].find_one({"_id": id})
            ) is not None:
                return updated_product

    if (
        existing_product := await request.app.mongodb['Products'].find_one({"_id": id})
    ) is not None:
        return existing_product

    raise HTTPException(status_code=404, detail=f"Product with id {id} not found")


@router.put('/{id}/image', response_description='Add an image')
async def add_image(id: str, request: Request,file: UploadFile):
    image_name= uuid4()
    with open(f"media/{image_name}.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    await request.app.mongodb['Products'].update_one({'_id': id}, {'$push':{'images': f'{image_name}.png'}})
    return {"success": True, "detail": "Successfully added a new image"}
