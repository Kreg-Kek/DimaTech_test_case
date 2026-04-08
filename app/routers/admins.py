from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_current_admin, get_db
from app import schemas, crud
from app.auth import hash_password

router = APIRouter(prefix="/admins", tags=["admins"])

@router.get("/me", response_model=schemas.UserRead)
async def read_admin_profile(admin = Depends(get_current_admin)):
    return admin

@router.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def admin_create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user_in.password)
    user_in.password = hashed
    user = await crud.create_user(db, user_in)
    await db.commit()
    return user

@router.put("/users/{user_id}", response_model=schemas.UserRead)
async def admin_update_user(user_id: int, payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    fields = {"email": payload.email, "full_name": payload.full_name}
    if payload.password:
        fields["password_hash"] = hash_password(payload.password)
    user = await crud.update_user(db, user_id, **fields)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    ok = await crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
    return

@router.get("/users", response_model=list[schemas.UserRead])
async def admin_list_users(db: AsyncSession = Depends(get_db)):
    users = await crud.list_users(db)
    return users

@router.get("/users/{user_id}/accounts", response_model=list[schemas.AccountRead])
async def admin_get_user_accounts(user_id: int, db: AsyncSession = Depends(get_db)):
    accounts = await crud.get_accounts_by_user(db, user_id)
    return accounts

