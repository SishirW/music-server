import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional,Set, Union 
from ..schemas import GetProductRating, CreateProduct,ProductQuestion,EditCategory ,CreateProductCategory, EditProduct, OptionalProduct, ProductRating, ShowProduct, ShowProductAdmin, ShowProductCategory, ShowUser, ShowUserWithId
from .user import get_current_user, validate_seller,validate_admin
import shutil
from uuid import uuid1, uuid4
from pydantic import parse_obj_as,Field


router= APIRouter(prefix= "/products",tags=["Musical products"])



@router.post('/',response_description="Add new product")
async def create_product(request: Request,product: CreateProduct,current_user: ShowUserWithId = Depends(validate_admin)):
    print(current_user)
    product.id= uuid.uuid4()
    product= jsonable_encoder(product)
    new_product= await request.app.mongodb['Products'].insert_one(product)
    #await request.app.mongodb['Products'].update(  {  $set : {"address":1} }  )
    await request.app.mongodb['Products'].update_one({'_id': new_product.inserted_id}, {'$set':{ 'avg_rating': 0.0,'no_of_rating':0 ,'rating':[],'questions':[]}})
    # for file in files:
    #     image_name= uuid4()
    #     with open(f"media/products/{image_name}.png", "wb") as buffer:
    #         shutil.copyfileobj(file.file, buffer)
        
    #     await request.app.mongodb['Products'].update_one({'_id': new_product.inserted_id}, {'$push':{'images': f'{image_name}.png'}})
    return {"success": True, "id":new_product.inserted_id}



@router.get('/',response_description='Get all products')
async def get_products(request: Request,page: int=1,sort:int=0,category: str=None,search:str=None,admin: bool=False):
    if page==0:
        page=1
    p=[]
    test={"has_next": False}
    if page is None: 
        page=0
    products_per_page=6
    if search !=None:
        if sort==0:
            products=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page)*products_per_page).limit(products_per_page)
        elif sort==1:
            products=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
        elif sort==2:
            products=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('points', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('points', -1).skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
        count=0
        
        async for product in product2:
            count+=1
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        async for product in products:
            p.append(product)
        test['products']=p
        return test
    if category !=None:
        if sort==0:
            products=request.app.mongodb['Products'].find({"category":category}).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find({"category":category}).skip((page)*products_per_page).limit(products_per_page)
        elif sort==1:
             products=request.app.mongodb['Products'].find({"category":category}).sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
             product2=request.app.mongodb['Products'].find({"category":category}).sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
        elif sort==2:
             products=request.app.mongodb['Products'].find({"category":category}).sort('points', -1).skip((page-1)*products_per_page).limit(products_per_page)
             product2=request.app.mongodb['Products'].find({"category":category}).sort('points', -1).skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['Products'].find({"category":category}).sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find({"category":category}).sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
        count=0
        count2=0
        async for product in product2:
            count+=1
        
        if count==0:
            test['has_next']=False
        else:
            test['has_next']=True
        
        
        async for product in products:
            p.append(product)
        test['products']=p
    
        return test
    products={}
    product2={}
    if sort==0:
        if admin:
            products=request.app.mongodb['Products'].find().skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find().skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['Products'].find().sort([('avg_rating',-1),('_id',1)]).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['Products'].find().sort([('avg_rating',-1),('_id',1)]).skip((page)*products_per_page).limit(products_per_page)
    elif sort==1:
        products=request.app.mongodb['Products'].find().sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['Products'].find().sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
    elif sort==2:
        products=request.app.mongodb['Products'].find().sort('points', -1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['Products'].find().sort('points', -1).skip((page)*products_per_page).limit(products_per_page)
    else:
        products=request.app.mongodb['Products'].find().sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['Products'].find().sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
    count=0
    
    async for product in product2:
        count+=1
    
    if count==0:
        test['has_next']=False
    else:
        test['has_next']=True
    
    
    async for product in products:
        p.append(product)
    test['products']=p
    return test
        #print(products)
        # products=await request.app.mongodb['Products'].find({"category":category}).to_list(1000)
        # if(len(products)==0):
        #     raise HTTPException(status_code=404, detail=f"Products with category {category} not found")
        

@router.get('/search/{value}',response_description='Get products by search', response_model=List[ShowProduct])
async def get_products(request: Request,value: str,page: int=0):
    p=[]
    if page is None: 
        page=0
    products_per_page=6
    
    
    products=await request.app.mongodb['Products'].find({"name":{"$regex":f".*{value}.*",'$options': 'i'}}).to_list(1000)
    print(products)
    if(len(products)==0):
        raise HTTPException(status_code=404, detail=f"Products with query {value} not found")
    
    return products

# @router.get('/admin',response_description='Get seller products', response_model=List[ShowProductAdmin])
# async def get_products_admin(request: Request,page: int=1,sort:int=0,category: str=None,search:str=None,current_user: ShowUserWithId = Depends(validate_admin)):
    


@router.get('/rate',response_description='View rating of Product',response_model=List[GetProductRating])
async def get_product_rating(request: Request, id:str):
    product=await request.app.mongodb['Products'].find_one({"_id": id})
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    ratings=product["rating"]
    _ratings=[]
    for rating in ratings:
        user=await request.app.mongodb['Users'].find_one({"_id": rating["user_id"]})
        if user is not None:
            rating["user_image"]="aa"
            rating["user_name"]=user["full_name"]
            rating.pop("user_id")
            _ratings.insert(0,rating)
    return _ratings

@router.get('/questions',response_description='View questions of Product')
async def get_product_questions(request: Request, id:str):
    product=await request.app.mongodb['Products'].find_one({"_id": id})
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    questions=product["questions"]
    _questions=[]
    for question in questions:
        user=await request.app.mongodb['Users'].find_one({"_id": question["user_id"]})
        if user is not None:
            question["user_image"]="aa"
            question["user_name"]=user["full_name"]
            question.pop("user_id")
            _questions.append(question)
    return _questions


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
async def edit_product(id: str, request: Request,product: EditProduct,current_user: ShowUserWithId = Depends(validate_admin)):
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

@router.put('/images/',response_description='Update Product image')
async def add_product_images(request: Request, files: List[UploadFile], current_user: ShowUserWithId = Depends(validate_admin)):
    names=[]
    if files is not None: 
        for file in files:
                image_name= uuid4()
                with open(f"media/products/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                names.append(f"{image_name}.png")
        return {"success":True, "images":names}
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
    
    product= await request.app.mongodb['Products'].find_one({"_id":pid})
    ratings=0.0
    count=0
    for rating in product['rating']:
        ratings=ratings+rating['rating']
        count+=1
    if ratings==0:
        avg=0
    else:
        avg= ratings/count
    r=await request.app.mongodb['Products'].update_one({'_id': pid}, {'$set':{'avg_rating': avg,'no_of_rating':count}})
    return {'success':True}

@router.put('/questions',response_description='Questions Product')
async def question_product(request: Request, questions: ProductQuestion,current_user: ShowUser = Depends(get_current_user)):
    questions= jsonable_encoder(questions)
    pid=questions['product_id']
    questions.pop('product_id')
    questions['user_id']=current_user['_id']
    if current_user['type']=='admin':
        questions['answer']=True
    else:
        questions['answer']=False
    r=await request.app.mongodb['Products'].update_one({'_id': pid}, {'$push':{'questions': questions}})
    #print(r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {'success':True}



@router.delete('/images/{id}')
async def delete_image(id: str, request: Request,images: List[str],current_user: ShowUser = Depends(get_current_user)): 
    empty=[]
    i=1
    for image in images:
        print(i)
        update_result=await request.app.mongodb['Products'].update_one({'_id': id}, {'$pull':{'images': image}})
        if os.path.exists(f"media/products/{image}"):
            os.remove(f"media/products/{image}")
        i=i+1
        if update_result.modified_count==0: 
            empty.append(image)
    if len(empty)==0: 
        return {"detail":"Successfully deleted image", "not_found":[]}
    else:
        return {"detail":"Some images were missing", "not_found":empty}

# Product Category

@router.get('/category/',response_description='Get all product categories')
async def get_product_categories(request: Request):
    categories=await request.app.mongodb['ProductCategory'].find().to_list(1000)
    #print(categories)
    return categories

@router.post('/category')
async def create_product_category(request: Request,category: CreateProductCategory, current_user: ShowUserWithId = Depends(validate_admin)):
    category.id= uuid.uuid4()
    category= jsonable_encoder(category)
    category['category']=category['category'].lower()
    new_category= await request.app.mongodb['ProductCategory'].insert_one(category)
    return {"success": True}

@router.delete('/category/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_category(id: str, request: Request,current_user: ShowUserWithId = Depends(validate_admin)):
    delete_product= await request.app.mongodb['ProductCategory'].delete_one({'_id': id})
    if delete_product.deleted_count==1:
        return {f"Successfully deleted product with id {id}"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {id} not found")



@router.put('/category/', response_description='Update Product')
async def edit_category(id: str, request: Request,product: EditCategory,current_user: ShowUserWithId = Depends(validate_admin)):
    #print('-----------------------------------------',product)
    product= {k: v for k, v in product.dict().items() if v is not None}
    
    
    if len(product) >= 1:
        
        update_result = await request.app.mongodb['ProductCategory'].update_one(
            {"_id": id}, {"$set": product}
        )
        

        if update_result.modified_count == 1:
            if (
                updated_product := await request.app.mongodb['ProductCategory'].find_one({"_id": id})
            ) is not None:
                return updated_product

    if (
        existing_product := await request.app.mongodb['ProductCategory'].find_one({"_id": id})
    ) is not None:
        return existing_product

    raise HTTPException(status_code=404, detail=f"Category with id {id} not found")

