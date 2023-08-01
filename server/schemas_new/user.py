from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

class EditUserSchema(BaseModel):
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)

class CreateUserSchema(EditUserSchema):
    password: str = Field(...)
    # verified: bool = False
    # type: str= "user"
    # location: Optional[str] = ''   #TODO
    # phone_no: Optional[str] = ''
    # devices: List[str]= []
    # points: int=0
    # social_links: SocialMedia