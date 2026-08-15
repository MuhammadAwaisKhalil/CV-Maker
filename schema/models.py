from pydantic import BaseModel,EmailStr
from typing import Optional

class UserRegisterSchema(BaseModel):
    full_name:str
    email:EmailStr
    password:str

class UserLoginSchema(BaseModel):
    email:EmailStr
    password:str

class TokenSchema(BaseModel):
    access_token:str
    token_type:str = "bearer"

class UserResponseSchema(BaseModel):
    id:int
    full_name:str
    email:str
    phone:Optional[str] = None
    linkedin_url:Optional[str]=None
    github_url:Optional[str]=None
    portfolio_url:Optional[str]=None

    class Config():
        from_attributes=True

