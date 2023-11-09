from typing import Optional, List
from pydantic import BaseModel, EmailStr,Field
from datetime import datetime

class CreateProductSchema(BaseModel):
    name: str= Field(...)
    price: float= Field(...)
    description: str= Field(...)
    category: List[str]= Field(...)
    #images: List[str]= Field(...)
    points: int= Field(...)

class EditProductSchema(BaseModel):
    name: Optional[str]
    price: Optional[float]
    description: Optional[str]
    category: Optional[List[str]]
    images: Optional[List[str]]
    points: Optional[int]
    is_featured: Optional[bool]

class CreateReviewSchema(BaseModel):
    product: str
    rating: int
    review: str

class CreateQuestionSchema(BaseModel):
    product: str
    question: str

class CreateQuestionResponseSchema(BaseModel):
    question_id :  str
    response: str