from fastapi import Request, HTTPException,APIRouter,status,Depends, UploadFile
from typing import List
from fastapi.encoders import jsonable_encoder
from server.db import get_database
from server.schemas_new.products import CreateProductSchema,EditProductSchema, CreateReviewSchema, CreateQuestionSchema, CreateQuestionResponseSchema
from ..utils.user import get_current_user, validate_admin
from server.schemas import ShowUserWithId
from server.models.products import delete_images, get_product_question,add_response_to_qn,add_question,get_product_review,add_review,add_product, edit_product, delete_product,add_images,get_product_byid,get_relevant_product
router = APIRouter(prefix="/product", tags=["Product"])



@router.post('/')
async def add_new_product(request: Request, product: CreateProductSchema, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result = await add_product(db, product,current_user['_id'])
    return jsonable_encoder(result)

@router.post('/review')
async def add_new_review(request: Request,review: CreateReviewSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_review(db, review, current_user['_id'])
    return jsonable_encoder(result)

@router.post('/question')
async def add_new_question(request: Request,question: CreateQuestionSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result = await add_question(db, question, current_user['_id'])
    return jsonable_encoder(result)

@router.get('/')
async def get_relevant_products(request: Request, page: int = 1,sort: int= 0,category: str = None, search: str = None):
    db = get_database(request)
    result = await get_relevant_product(db,page,category, search, sort)
    return jsonable_encoder(result)

@router.get('/review')
async def get_product_reviews(request: Request, id:str,page: int = 1):
    db = get_database(request)
    result = await get_product_review(db,id,page)
    return jsonable_encoder(result)

@router.get('/question')
async def get_product_questions(request: Request, id:str,page: int = 1):
    db = get_database(request)
    result = await get_product_question(db,id,page)
    return jsonable_encoder(result)

@router.get('/{id}')
async def get_product_by_id(id: str, request: Request):
    db = get_database(request)
    result = await get_product_byid(db, id)
    return jsonable_encoder(result)

@router.put('/', response_description='Update product')
async def edit_products(request: Request, product: EditProductSchema, id: str, current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await edit_product(db,id, product)
    return jsonable_encoder(result)

@router.put('/response_to_qn', response_description='Update product question')
async def add_response_to_qns(request: Request, question: CreateQuestionResponseSchema, current_user: ShowUserWithId = Depends(get_current_user)):
    db = get_database(request)
    result=await add_response_to_qn(db, question, current_user["_id"])
    return jsonable_encoder(result)


@router.put('/images', response_description='Update product image')
async def add_product_images(request: Request, files: List[UploadFile],id: str,current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    product=await get_product_byid(db,id)
    result = await add_images(db, id,files)
    return jsonable_encoder(result)

@router.delete('/images', response_description='Update product image')
async def delete_product_images(request: Request, files: List[str],id: str,current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    product=await get_product_byid(db,id)
    result = await delete_images(db, id,files)
    return jsonable_encoder(result)

@router.delete('/{id}', response_description='Delete product package',status_code=status.HTTP_204_NO_CONTENT)
async def delete_products(request: Request, id:str,current_user: ShowUserWithId = Depends(validate_admin)):
    db = get_database(request)
    result=await delete_product(db, id)
    return jsonable_encoder(result)

