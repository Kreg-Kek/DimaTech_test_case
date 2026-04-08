from pydantic import BaseModel, EmailStr, condecimal
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str]

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
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

class AccountRead(BaseModel):
    id: int
    user_id: int
    balance: condecimal(max_digits=18, decimal_places=2)
    class Config:
        orm_mode = True

class PaymentCreate(BaseModel):
    uid: str
    account_id: int
    amount: condecimal(max_digits=18, decimal_places=2)

class PaymentRead(BaseModel):
    id: int
    uid: str
    account_id: int
    amount: condecimal(max_digits=18, decimal_places=2)
    class Config:
        orm_mode = True