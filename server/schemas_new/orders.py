from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class Product(BaseModel):
    product: str
    quantity: int
    price: float

class PaymentSchema(BaseModel):
    khalti_token : str
    idx: str
    phone: str
    amount: float
    #order: str
class PlaceOrder(BaseModel):
    products: List[Product] 
    type: int
    payment: Optional[PaymentSchema]