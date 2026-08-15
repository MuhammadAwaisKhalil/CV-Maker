import sqlite3
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from db.database import get_db
from schema.models import UserRegisterSchema, TokenSchema, UserResponseSchema, UserLoginSchema
from auth.utils import hash_password, verify_password, create_access_token, get_current_user_id
from db.utils import get_user_by_email, get_user_by_id, create_user

auth_router = APIRouter(prefix="/auth")
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload:UserRegisterSchema):
    """Regitser user endpoint"""

    if get_user_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="The account already exists")

    hashed_password = hash_password(payload.password)

    user_id = create_user(payload.full_name,payload.email,hashed_password)

    return {"message":"User registered","user_id":user_id}

@auth_router.post("/login", response_model=TokenSchema)
def login_user(payload:UserLoginSchema):
    user = get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect credentials")

    user_id = user["id"]
    access_token = create_access_token(user_id)

    return {"access_token":access_token, "token_type":"bearer"}


@auth_router.get("/me", response_model=UserResponseSchema)
def get_me(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    return user
