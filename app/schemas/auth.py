from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    field_validator
)

class SignupRequest(BaseModel):
    email: EmailStr

    password: str=Field(min_length=12, max_length=128)

class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str=Field(min_length=12, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value:str) -> str:
        return str(value).strip().lower()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str="Bearer"

class RefreshRequest(BaseModel):
    refresh_token:str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class MessageResponse(BaseModel):
    message: str




    

    
