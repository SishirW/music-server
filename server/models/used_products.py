from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr,Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os
from .product_category import check_productcategory_exists
from server.schemas_new.products import CreateQuestionSchema, CreateQuestionResponseSchema
from server.schemas_new.used_products import RequestToBuy

collection_name= 'UsedProducts'
question_collection_name= 'UsedProductsQuestions'
request_collection_name= 'UsedProductsRequests'

class UsedProduct(BaseModel):
    name: str
    price: float
    description: str
    category: List[str]
    images: List[str]=[]
    user: str

class UsedProductQuestion(BaseModel):
    questioneer: str
    product: str
    question: str
    response: str= None
    response_user: str= None

class UsedProductRequest(BaseModel):
    product: str
    name: str
    phone_no: int
    location: str
    user: str

async def add_product(db, product, user):
    category= [x for x in product.category if await check_productcategory_exists(x,db)]
    product1= UsedProduct(
       name= product.name,
       price= product.price,
       description= product.description,
       category= category,
       user= user
   )
    encoded = jsonable_encoder(product1)
    add_product= await db[collection_name].insert_one(encoded)
    detail= await db[collection_name].find_one({'_id': add_product.inserted_id})
    return detail

async def add_images(db,product_id, files):
    names = []
    if files is not None:
        for file in files:
            image_name = uuid.uuid4()
            os.makedirs(f'media_new/used_product/{product_id}', exist_ok=True)
            with open(f"media_new/used_product/{product_id}/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            names.append(f"{image_name}.png")
        db[collection_name].update_one({'_id': product_id}, {'$push': {'images': {'$each':names}}})
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')

async def get_relevant_product(db,page,category, search):
    if search != None:
        pipeline= get_search_pipeline(search, page)  
        product =await db[collection_name].aggregate(pipeline).to_list(20)
    elif category != None:
        pipeline= get_category_pipeline(category, page)  
        product =await db[collection_name].aggregate(pipeline).to_list(20)
    else:
      pipeline= get_pipeline(page)  
      product =await db[collection_name].aggregate(pipeline).to_list(20)
    return product


async def get_product_byid(db, id):
    product = await db[collection_name].find_one({"_id": id})
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"product not found!")
    return product

async def get_user_product(db, user):
    product = await db[collection_name].find({"user": user}).to_list(None)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"product not found!")
    return product

async def check_product_exists(db, id):
    artist = await db[collection_name].find_one({"_id": id})
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"product not found!")
    return artist

async def add_question(db, question: CreateQuestionSchema, user):
    product= await check_product_exists(db, question.product)

    question= UsedProductQuestion(
        questioneer= user,
        product= question.product,
        question= question.question
    )
    encoded = jsonable_encoder(question)
    await db[question_collection_name].insert_one(encoded)
    return {'success': True}

async def request_for_buying(db, buying: RequestToBuy, user):
    product= await check_product_exists(db, buying.product_id)

    question= UsedProductRequest(
        product=buying.product_id,
        name= buying.name,
        phone_no= buying.phone_no,
        location= buying.location,
        user= user
    )
    encoded = jsonable_encoder(question)
    await db[request_collection_name].insert_one(encoded)
    return {'success': True}



async def add_response_to_qn(db, question: CreateQuestionResponseSchema, user):
    update_result =await db[question_collection_name].update_one(
            {"_id": question.question_id}, {"$set": {"response": question.response, "response_user":user}}
        )
    if update_result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f'Question not found')
    return {'success': True}

async def delete_images(db, id, files):
    empty=[]
    for image in files:
        update_result= await db[collection_name].update_one({'_id': id}, {'$pull': {'images': image}})
        if update_result.modified_count == 0:
            empty.append(image)
    if len(empty) == 0:
        return {"detail": "Successfully deleted image", "not_found": []}
    else:
        return {"detail": "Some images were missing", "not_found": empty}


async def get_product_question(db, id,page):
    product= await check_product_exists(db, id)
    pipeline= get_product_question_pipeline(id, page)  
    questions =await db[question_collection_name].aggregate(pipeline).to_list(20)
    return questions

async def get_product_request(db, id,page):
    product= await check_product_exists(db, id)
    pipeline= get_product_request_pipeline(id, page)  
    questions =await db[request_collection_name].aggregate(pipeline).to_list(20)
    return questions


async def delete_product(db, product_id, user, type):
    check= await get_product_byid(db, product_id)
    if not check:
        raise HTTPException(status_code=404, detail=f"product not found")
    if check['user']== user or type=='admin':
        product=await db[collection_name].delete_one({'_id': product_id})
        if product.deleted_count == 1:
            return {f"Successfully deleted product"}
        else:
            raise HTTPException(status_code=404, detail=f"product not found")
    raise HTTPException(status_code=404, detail=f"product not found")

def get_product_question_pipeline(id, page):
    return [
      {
            "$match": {
                "product": id
            }
        },
        {
    "$lookup": {
      "from": "Users",
      "localField": "questioneer",
      "foreignField": "_id",
      "as": "user_details"
    }
        },
        {
    "$lookup": {
      "from": "Users",
      "localField": "response_user",
      "foreignField": "_id",
      "as": "response_user_details"
    }
        },
        
        {
            "$project": {
                "_id": 1,
                "questioneer": 1,
                "product": 1,
                "question": 1,
                "response":1,
                "response_user":1,
                "question_username": "$user_details.username",
                "response_username": "$response_user_details.username",
                
            }
        },
        
  {
  "$skip": (page-1)*20
  },
  {
  "$limit": 20
  }
]


def get_product_request_pipeline(id, page):
    return [
      {
            "$match": {
                "product": id
            }
        },
        {
    "$lookup": {
      "from": "Users",
      "localField": "user",
      "foreignField": "_id",
      "as": "user_details"
    }
        },
        
        
        
  {
  "$skip": (page-1)*20
  },
  {
  "$limit": 20
  }
]

def get_pipeline(page):    
    return [
        {
            "$lookup": {
                "from": "ProductReview",
                "localField": "_id",
                "foreignField": "product",
                "as": "reviews"
            }
        },
       {
            "$addFields": {
                "average_rating": {
                    "$ifNull": [
                        {"$avg": "$reviews.rating"},
                        0
                    ]
                }
            }
        },
        {
            "$unset": "reviews"  
        },
        {
  "$skip": (page-1)*20
  },
  {
  "$limit": 20
  }
    ]


def get_search_pipeline(keyword, page):    
    return [
      {
  "$match": {
    "name": {
      "$regex": f".*{keyword}.*",
      "$options": "i"
    },
  }
  },
  
  
  
  {
  "$skip": (page-1)*20
  },
  {
  "$limit": 20
  }
]
  
  

def get_category_pipeline(category, page):
    return [
      {
            "$match": {
                "category": {
                    "$in": [category]
                },
               
            }
        },
        
        
  
  {
  "$skip": (page-1)*20
  },
  {
  "$limit": 20
  }
]
    