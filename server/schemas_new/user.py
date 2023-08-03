from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class EditUserSchema(BaseModel):
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)

class CreateUserSchema(EditUserSchema):
    password: str = Field(...)