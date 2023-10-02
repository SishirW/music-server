from . import BaseModel
from typing import List
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import uuid, shutil, os
# from .product_category import check_productcategory_exists
# from server.schemas_new.products import EditProductSchema, CreateReviewSchema, CreateQuestionSchema, CreateQuestionResponseSchema


collection_name= 'Orders'
