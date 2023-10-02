from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class AddToCart(BaseModel):
    product: str= Field(...)
    count: int= Field(...)