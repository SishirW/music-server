from typing import Optional
from pydantic import BaseModel, Field

class AddProductCategorySchema(BaseModel):
    name: str = Field("restaurant")
    display_name: str = Field('Restaurant')
    image: Optional[str] = Field('base64 icon')

