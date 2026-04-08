from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_current_user, get_db
from app import schemas, crud

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.UserRead)
async def read_own_profile(current = Depends(get_current_user)):
    return current["user"]

@router.get("/me/accounts", response_model=list[schemas.AccountRead])
async def list_my_accounts(current = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = current["user"]
    accounts = await crud.get_accounts_by_user(db, user.id)
    return accounts

@router.get("/me/payments", response_model=list[schemas.PaymentRead])
async def list_my_payments(current = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = current["user"]
    payments = await crud.get_payments_by_user(db, user.id)
    return payments
