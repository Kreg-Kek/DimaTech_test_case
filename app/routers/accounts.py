from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_session

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=schemas.AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(account_in: schemas.AccountCreate, db: AsyncSession = Depends(get_session)):
    user = await crud.get_user(db, account_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    account = await crud.create_account(db, account_in)
    await db.commit()
    return account

@router.get("/{account_id}", response_model=schemas.AccountRead)
async def read_account(account_id: int, db: AsyncSession = Depends(get_session)):
    account = await crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account