import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional,Set, Union 
from ..schemas import GetProductRating, CreateProduct, CreateProductCategory, EditProduct, OptionalProduct, ProductRating, ShowProduct, ShowProductAdmin, ShowProductCategory, ShowUser, ShowUserWithId
from .user import get_current_user, validate_seller
import shutil
from uuid import uuid1, uuid4
from pydantic import parse_obj_as,Field


router= APIRouter(prefix= "/products",tags=["Musical products"])



@router.post('/',response_description="Add new product")
async def create_product(request: Request,product: CreateProduct,current_user: ShowUserWithId = Depends(validate_seller)):
    print(current_user)
    product.id= uuid.uuid4()
    product= jsonable_encoder(product)
    
    new_product= await request.app.mongodb['Products'].insert_one(product)
    #await request.app.mongodb['Products'].update(  {  $set : {"address":1} }  )
    await request.app.mongodb['Products'].update_one({'_id': new_product.inserted_id}, {'$set':{'images': [],'seller_id':current_user['_id'],'rating':[]}})
    # for file in files:
    #     image_name= uuid4()
    #     with open(f"media/products/{image_name}.png", "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
        
    #     await request.app.mongodb['Products'].update_one({'_id': new_product.inserted_id}, {'$push':{'images': f'{image_name}.png'}})
    return {"success": True, "id":new_product.inserted_id}



@router.get('/',response_description='Get all products', response_model=List[ShowProduct])
async def get_products(request: Request,page: int=0,category: str=None):
    p=[]
    if page is None: 
        page=0
    products_per_page=6
    
    if category is None:
        products=request.app.mongodb['Products'].find().skip(page*products_per_page).limit(products_per_page)
        async for product in products:
            p.append(product)
        #print(products)
    else: 
        products=await request.app.mongodb['Products'].find({"category":category}).to_list(1000)
        if(len(products)==0):
            raise HTTPException(status_code=404, detail=f"Products with category {category} not found")
    
    return parse_obj_as(List[ShowProduct],p)

@router.get('/seller',response_description='Get seller products', response_model=List[ShowProductAdmin])
async def get_products(request: Request,current_user: ShowUser = Depends(validate_seller)):
    products=await request.app.mongodb['Products'].find({"seller_id":current_user['_id']}).to_list(1000)
    return products


@router.get('/rate',response_description='View rating of Product',response_model=List[GetProductRating])
async def get_product_rating(request: Request, id:str,current_user: ShowUser = Depends(get_current_user)):
    product=await request.app.mongodb['Products'].find_one({"_id": id})
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    ratings=product["rating"]
    _ratings=[]
    for rating in ratings:
        user=await request.app.mongodb['Users'].find_one({"_id": rating["user_id"]})
        rating["user_image"]="aa"
        rating["user_name"]=user["full_name"]
        rating.pop("user_id")
        _ratings.insert(0,rating)
    return _ratings


@router.get('/{id}', response_model=ShowProduct)
async def get_product_by_id(id: str, request: Request):
    
    product= await request.app.mongodb['Products'].find_one({"_id":id})
    #print('---------------',product)
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




@router.put('/', response_description='Update Product', response_model=ShowProduct)
async def edit_product(id: str, request: Request,product: EditProduct,current_user: ShowUserWithId = Depends(validate_seller)):
    #print('-----------------------------------------',product)
    product= {k: v for k, v in product.dict().items() if v is not None}
    
    
    if len(product) >= 1:
        
        update_result = await request.app.mongodb['Products'].update_one(
            {"_id": id}, {"$set": product}
        )
        

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

@router.put('/images/{id}',response_description='Update Product image')
async def add_product_images(request: Request, id: str, files: List[UploadFile]):
    if files is not None: 
        for file in files:
                image_name= uuid4()
                with open(f"media/products/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                update_result=await request.app.mongodb['Products'].update_one({'_id': id}, {'$push':{'images': f'{image_name}.png'}})
                if update_result.matched_count==0: 
                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Product with id {id} not found')
        return {"Successfully added new images"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')

@router.put('/rate',response_description='Rate Product')
async def rate_product(request: Request, rating: ProductRating,current_user: ShowUser = Depends(get_current_user)):
    rating= jsonable_encoder(rating)
    pid=rating['product_id']
    rating.pop('product_id')
    rating['user_id']=current_user['_id']
    r=await request.app.mongodb['Products'].update_one({'_id': pid}, {'$push':{'rating': rating}})
    #print(r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {'sucess':True}



@router.delete('/images/{id}')
async def delete_image(id: str, request: Request,images: List[str],current_user: ShowUser = Depends(get_current_user)): 
    
    empty=[]
    for image in images:
        update_result=await request.app.mongodb['Products'].update_one({'_id': id}, {'$pull':{'images': image}})
        os.remove(f"media/products/{image}")
        if update_result.modified_count==0: 
            empty.append(image)
    if len(empty)==0: 
        return {"detail":"Successfully deleted image", "not_found":[]}
    else:
        return {"detail":"Some images were missing", "not_found":empty}

# Product Category

@router.get('/category/',response_description='Get all product categories', response_model=List[ShowProductCategory])
async def get_product_categories(request: Request):
    categories=await request.app.mongodb['ProductCategory'].find().to_list(1000)
    #print(categories)
    return categories

@router.post('/category')
async def create_product_category(request: Request,category: CreateProductCategory):
    category.id= uuid.uuid4()
    category= jsonable_encoder(category)
    new_category= await request.app.mongodb['ProductCategory'].insert_one(category)
    return {"success": True}

@router.delete('/category/{name}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_category(name: str, request: Request):
    delete_product= await request.app.mongodb['ProductCategory'].delete_one({'category': name})
    if delete_product.deleted_count==1:
        return {f"Successfully deleted product with name {name}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with name {name} not found")


#Product Card
