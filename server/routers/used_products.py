import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, Response, UploadFile, Request, Body, status,BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List, Optional,Set, Union 
from .user import get_current_user, validate_seller,validate_admin
from ..schemas import CreateUsedProduct,ShowUserWithId,ShowUsedProduct,EditUsedProduct,ProductQuestion, RequestToBuy,GetUsedProduct,GetUsedProductAdmin
import shutil
from uuid import uuid1, uuid4
from pydantic import parse_obj_as,Field
from ..background_tasks import send_notification
from datetime import datetime


router= APIRouter(prefix= "/used-products",tags=["Used products"])

@router.post('/',response_description="Add new used product")
async def create_product(request: Request,background_tasks: BackgroundTasks,product: CreateUsedProduct,current_user: ShowUserWithId = Depends(get_current_user)):
    print(current_user)
    product.id= uuid.uuid4()
    product= jsonable_encoder(product)
    
    new_product= await request.app.mongodb['UsedProducts'].insert_one(product)
    #await request.app.mongodb['Products'].update(  {  $set : {"address":1} }  )
    await request.app.mongodb['UsedProducts'].update_one({'_id': new_product.inserted_id}, {'$set':{'seller_id':current_user['_id'], 'seller_email': current_user['email'],'date_added':datetime.now(),'questions':[],'requests_to_buy':[]}})

    admin= await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)
    
    devices=[]
    for users in admin:
        devices.extend(users['devices'])
    background_tasks.add_task(send_notification,tokens=devices, detail={},type='new-used-product',title='Used Product',body='User {} has added a new second hand product.'.format(current_user['full_name']))
    return {"success": True, "id":new_product.inserted_id}


@router.get('/',response_description='Get all used products',response_model=GetUsedProduct)
async def get_products(request: Request,page: int=1,sort:int=0,category: str=None,search:str=None):
    if page==0:
        page=1
    p=[]
    test={"has_next": False}
    if page is None: 
        page=0
    products_per_page=10
    print(category)
    if search !=None:
        if sort==0:
            products=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page)*products_per_page).limit(products_per_page)
        elif sort==1:
            products=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
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
            products=request.app.mongodb['UsedProducts'].find({"category":category}).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"category":category}).skip((page)*products_per_page).limit(products_per_page)
        elif sort==1:
             products=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
             product2=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
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
        products=request.app.mongodb['UsedProducts'].find().skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['UsedProducts'].find().skip((page)*products_per_page).limit(products_per_page)
    elif sort==1:
        products=request.app.mongodb['UsedProducts'].find().sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['UsedProducts'].find().sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
    else:
        products=request.app.mongodb['UsedProducts'].find().sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['UsedProducts'].find().sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
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

@router.get('/admin',response_description='Get all used products',response_model=GetUsedProductAdmin)
async def get_products(request: Request,page: int=1,sort:int=0,category: str=None,search:str=None,current_user: ShowUserWithId = Depends(validate_admin)):
    if page==0:
        page=1
    p=[]
    test={"has_next": False}
    if page is None: 
        page=0
    products_per_page=10
    print(category)
    if search !=None:
        if sort==0:
            products=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).skip((page)*products_per_page).limit(products_per_page)
        elif sort==1:
            products=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"name":{"$regex":f".*{search}.*",'$options': 'i'}}).sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
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
            products=request.app.mongodb['UsedProducts'].find({"category":category}).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"category":category}).skip((page)*products_per_page).limit(products_per_page)
        elif sort==1:
             products=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
             product2=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
        else:
            products=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
            product2=request.app.mongodb['UsedProducts'].find({"category":category}).sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
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
        products=request.app.mongodb['UsedProducts'].find().sort('date_added',-1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['UsedProducts'].find().sort('date_added',-1).skip((page)*products_per_page).limit(products_per_page)
    elif sort==1:
        products=request.app.mongodb['UsedProducts'].find().sort('price', 1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['UsedProducts'].find().sort('price', 1).skip((page)*products_per_page).limit(products_per_page)
    else:
        products=request.app.mongodb['UsedProducts'].find().sort('price', -1).skip((page-1)*products_per_page).limit(products_per_page)
        product2=request.app.mongodb['UsedProducts'].find().sort('price', -1).skip((page)*products_per_page).limit(products_per_page)
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
@router.get('/my-used-products',response_description='Get user used products')
async def get_my_products(request: Request,current_user: ShowUserWithId = Depends(get_current_user)):
    products=await request.app.mongodb['UsedProducts'].find({"seller_id": current_user['_id']}).to_list(1000000)
    return products
@router.get('/questions',response_description='View questions of used Product')
async def get_product_questions(request: Request, id:str):
    product=await request.app.mongodb['UsedProducts'].find_one({"_id": id})
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


@router.get('/{id}',response_model=ShowUsedProduct)
async def get_product_by_id(id: str, request: Request):
    
    product= await request.app.mongodb['UsedProducts'].find_one({"_id":id})
    #print('---------------',product)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    return product

@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(id: str, request: Request,current_user: ShowUserWithId = Depends(get_current_user)):
    product= await request.app.mongodb['UsedProducts'].find_one({"_id":id})
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    if product['seller_id']== current_user['_id'] or current_user['type']=='admin':
        delete_product= await request.app.mongodb['UsedProducts'].delete_one({'_id': id})
        return {f"Successfully deleted product with id {id}"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.put('/', response_description='Update Product', response_model=ShowUsedProduct)
async def edit_product(id: str, request: Request,product: EditUsedProduct,current_user: ShowUserWithId = Depends(get_current_user)):
    #print('-----------------------------------------',product)
    product_check= await request.app.mongodb['UsedProducts'].find_one({"_id":id})
    if product_check is None:
          raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    if product_check['seller_id']!= current_user['_id']:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )

    product= {k: v for k, v in product.dict().items() if v is not None}
    
    
    if len(product) >= 1:
        
        update_result = await request.app.mongodb['UsedProducts'].update_one(
            {"_id": id}, {"$set": product}
        )
        

        if update_result.modified_count == 1:
            if (
                updated_product := await request.app.mongodb['UsedProducts'].find_one({"_id": id})
            ) is not None:
                return updated_product

    if (
        existing_product := await request.app.mongodb['UsedProducts'].find_one({"_id": id})
    ) is not None:
        return existing_product

    raise HTTPException(status_code=404, detail=f"Product with id {id} not found")


@router.put('/images/',response_description='Update used Product image')
async def add_product_images(request: Request, files: List[UploadFile],current_user: ShowUserWithId = Depends(get_current_user)):
    names=[]
    if files is not None: 
        for file in files:
                image_name= uuid.uuid4()
                with open(f"media/used_products/{image_name}.png", "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                names.append(f"{image_name}.png")
        return {"success":True, "images":names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No image was added')

@router.delete('/images/')
async def delete_image(id: str, request: Request,images: List[str],current_user: ShowUserWithId = Depends(get_current_user)): 
    product_check= await request.app.mongodb['UsedProducts'].find_one({"_id":id})
    if product_check is None:
          raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    if product_check['seller_id']!= current_user['_id']:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    empty=[]
    for image in images:
        update_result=await request.app.mongodb['UsedProducts'].update_one({'_id': id}, {'$pull':{'images': image}})
        if os.path.exists(f"media/used_products/{image}"):
            os.remove(f"media/used_products/{image}")
       
        if update_result.modified_count==0: 
            empty.append(image)
    if len(empty)==0: 
        return {"detail":"Successfully deleted image", "not_found":[]}
    else:
        return {"detail":"Some images were missing", "not_found":empty}


@router.put('/questions',response_description='Questions Used Product')
async def question_product(request: Request, questions: ProductQuestion,current_user: ShowUserWithId = Depends(get_current_user)):
    questions= jsonable_encoder(questions)
    pid=questions['product_id']
    questions.pop('product_id')
    questions['user_id']=current_user['_id']
    print(pid)
    product_check= await request.app.mongodb['UsedProducts'].find_one({"_id":pid})
    if product_check is None:
          raise HTTPException(status_code=404, detail=f"Product with id {pid} not found")
    print(product_check)
    if current_user['_id']==product_check['seller_id']:
        questions['answer']=True
    else:
        questions['answer']=False
    r=await request.app.mongodb['UsedProducts'].update_one({'_id': pid}, {'$push':{'questions': questions}})
    #print(r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {'success':True}

@router.put('/request-to-buy',response_description='Request to buy Used Product')
async def request_to_buy(request: Request, id: str,request_to_buy: RequestToBuy,background_tasks: BackgroundTasks,current_user: ShowUserWithId = Depends(get_current_user)):
    request_to_buy= jsonable_encoder(request_to_buy)
    product_check= await request.app.mongodb['UsedProducts'].find_one({"_id":id})
    if product_check is None:
          raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    request_to_buy['user_id']=current_user['_id']
    request_to_buy['email']=current_user['email']
    r=await request.app.mongodb['UsedProducts'].update_one({'_id': id}, {'$push':{'requests_to_buy': request_to_buy}})
    #print(r.modified_count)
    if r.modified_count==0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    admin= await request.app.mongodb['Users'].find({'type': 'admin'}).to_list(1000000)
    devices=[]
    for users in admin:
        devices.extend(users['devices'])
    product_check= await request.app.mongodb['UsedProducts'].find_one({"_id":id})
    product_check.pop('date_added')
    background_tasks.add_task(send_notification,tokens=devices, detail={'requests':product_check['requests_to_buy'], 'product':product_check},type='used-product-request',title='Used Product Request',body='User {} has requested to buy {}'.format(current_user['full_name'], product_check['name']))
    return {'success':True}


