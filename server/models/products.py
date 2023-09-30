from . import BaseModel
from typing import List, Optional
from pydantic import EmailStr,Field
from .bands import Location
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os
from .product_category import check_productcategory_exists
from server.schemas_new.products import EditProductSchema, CreateReviewSchema, CreateQuestionSchema, CreateQuestionResponseSchema


collection_name= 'Products'
review_collection_name= 'ProductReview'
question_collection_name= 'ProductQuestion'

class Product(BaseModel):
    name: str
    price: float
    description: str
    category: List[str]
    images: List[str]
    points: int

class ProductReview(BaseModel):
    reviewer: str
    product: str
    rating: int
    review: str

class ProductQuestion(BaseModel):
    questioneer: str
    product: str
    question: str
    response: str= None
    response_user: str= None

async def add_product(db, product, user):
    category= [x for x in product.category if await check_productcategory_exists(x,db)]
    product1= Product(
       name= product.name,
       price= product.price,
       description= product.description,
       images= product.images,
       points=product.points,
       category= category
   )
    encoded = jsonable_encoder(product1)
    await db[collection_name].insert_one(encoded)
    return {'success': True}



async def get_product_byid(db, id):
    product = await db[collection_name].find_one({"_id": id})
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

async def get_relevant_product(db,page,category, search):
    if search != None:
        pipeline= get_search_pipeline(search, page)  
        product =await db[collection_name].aggregate(pipeline).to_list(5)
    elif category != None:
        pipeline= get_category_pipeline(category, page)  
        product =await db[collection_name].aggregate(pipeline).to_list(5)
    else:
      product = await db[collection_name].find().skip(
        (page-1)*5).limit(5).to_list(6)
    return product



async def add_images(db,product_id, files):
    names = []
    if files is not None:
        for file in files:
            image_name = uuid.uuid4()
            os.makedirs(f'media_new/product/{product_id}', exist_ok=True)
            with open(f"media_new/product/{product_id}/{image_name}.png", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            names.append(f"{image_name}.png")
        db[collection_name].update_one({'_id': product_id}, {'$push': {'images': {'$each':names}}})
        return {"success": True, "images": names}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail='No image was added')

async def edit_product(db,product_id,product: EditProductSchema):
    product = {k: v for k, v in product.dict().items() if v is not None}
    check= await check_product_exists(db, product_id)
    if not check:
        raise HTTPException(status_code=404, detail=f"product not found")
    if len(product) >= 1:

        update_result = await db[collection_name].update_one(
            {"_id": product_id}, {"$set": product}
        )

        if update_result.modified_count == 1:
            if (
                updated_product := await db[collection_name].find_one({"_id": product_id})
            ) is not None:
                return updated_product

    if (
        existing_product := await db[collection_name].find_one({"_id": product_id})
    ) is not None:
        return existing_product

    raise HTTPException(status_code=404, detail=f"Package with id {product_id} not found")

async def delete_product(db, product_id):
    check= await check_product_exists(db, product_id)
    if not check:
        raise HTTPException(status_code=404, detail=f"product not found")
    product=await db[collection_name].delete_one({'_id': product_id})
    if product.deleted_count == 1:
        return {f"Successfully deleted product"}
    else:
        raise HTTPException(status_code=404, detail=f"product not found")
    
async def add_review(db, review: CreateReviewSchema, user):
    product= await check_product_exists(db, review.product)

    review= ProductReview(
        reviewer= user,
        product= review.product,
        rating= review.rating,
        review= review.review
    )
    encoded = jsonable_encoder(review)
    await db[review_collection_name].insert_one(encoded)
    return {'success': True}

async def add_question(db, question: CreateQuestionSchema, user):
    product= await check_product_exists(db, question.product)

    question= ProductQuestion(
        questioneer= user,
        product= question.product,
        question= question.question
    )
    encoded = jsonable_encoder(question)
    await db[question_collection_name].insert_one(encoded)
    return {'success': True}

async def add_response_to_qn(db, question: CreateQuestionResponseSchema, user):
    update_result =await db[question_collection_name].update_one(
            {"_id": question.question_id}, {"$set": {"response": question.response, "response_user":user}}
        )
    if update_result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f'Question not found')
    return {'success': True}


async def get_product_review(db, id,page):
    product= await check_product_exists(db, id)
    pipeline= get_product_review_pipeline(id, page)  
    reviews =await db[review_collection_name].aggregate(pipeline).to_list(5)
    return reviews

async def get_product_question(db, id,page):
    product= await check_product_exists(db, id)
    pipeline= get_product_question_pipeline(id, page)  
    questions =await db[question_collection_name].aggregate(pipeline).to_list(5)
    return questions


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
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
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
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
]
    

def get_product_review_pipeline(id, page):
    return [
      {
            "$match": {
                "product": id
            }
        },
        {
    "$lookup": {
      "from": "Users",
      "localField": "reviewer",
      "foreignField": "_id",
      "as": "user_details"
    }
        },
        {
            "$unwind": "$user_details"
        },
        {
            "$project": {
                "_id": 1,
                "reviewer": 1,
                "venue": 1,
                "rating": 1,
                "review": 1,
                "username": "$user_details.username"
            }
        },
        
  {
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
]


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
  "$skip": (page-1)*5
  },
  {
  "$limit": 5
  }
]