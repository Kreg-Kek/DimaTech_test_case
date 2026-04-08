from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_session

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_session)):
    user = await crud.create_user(db, user_in)
    await db.commit()
    return user

@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_session)):
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user