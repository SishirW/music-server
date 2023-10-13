from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from server.models.user import SocialMedia

class EditUserSchema(BaseModel):
    full_name: Optional[str]
    #username: Optional[str]
    location: Optional[str]
    phone_no: Optional[str]
    social_links: Optional[SocialMedia]

class CreateUserSchema(BaseModel):
    full_name: str = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)