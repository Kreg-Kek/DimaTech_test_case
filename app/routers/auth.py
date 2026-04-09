from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app import schemas, crud
from app.database import get_session
from app.auth import verify_password, hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    auth = await crud.authenticate_user(db, form_data.username, form_data.password, verify_password)
    if not auth:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    if auth["type"] == "admin":
        subject = auth["obj"].email
        token = create_access_token(subject=subject, is_admin=True)
    else:
        subject = auth["obj"].email
        token = create_access_token(subject=subject, is_admin=False)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_session)):
    existing = await crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user_in.password)
    user_in.password = hashed
    user = await crud.create_user(db, user_in)
    await db.commit()
    return user
