from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal
from typing_extensions import Annotated 

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str]
    is_admin: Optional[bool] = False

class AuthIn(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    class Config:
        orm_mode = True

class AccountRead(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    class Config:
        orm_mode = True

class PaymentRead(BaseModel):
    id: int
    uid: str
    account_id: int
    amount: Decimal
    class Config:
        orm_mode = True

class AdminCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str]

class AdminRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    class Config:
        orm_mode = True

class AccountCreate(BaseModel):
    user_id: int



class PaymentCreate(BaseModel):
    uid: str
    account_id: int
    amount: Decimal

class WebhookPayload(BaseModel):
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    signature: str