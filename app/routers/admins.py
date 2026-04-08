from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_session

router = APIRouter(prefix="/admins", tags=["admins"])

@router.post("/", response_model=schemas.AdminRead, status_code=status.HTTP_201_CREATED)
async def create_admin(admin_in: schemas.AdminCreate, db: AsyncSession = Depends(get_session)):
    admin = await crud.create_admin(db, admin_in)
    await db.commit()
    return admin
