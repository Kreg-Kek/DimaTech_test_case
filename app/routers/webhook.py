from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib

from .. import schemas, crud
from ..database import get_session
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY=getenv('SECRET_KEY')

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/payment")
async def payment_webhook(payload: schemas.WebhookPayload, db: AsyncSession = Depends(get_session)):
    sign_str = f"{payload.account_id}{payload.amount}{payload.transaction_id}{payload.user_id}{SECRET_KEY}"
    expected = hashlib.sha256(sign_str.encode()).hexdigest()
    if expected != payload.signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    user = await crud.get_user(db, payload.user_id)
    if not user:
        user = await crud.create_user(db, schemas.UserCreate(email=f"user{payload.user_id}@local", password="changeme", full_name=None))

    account = await crud.get_or_create_account(db, owner_id=user.id, account_id=payload.account_id)

    amount = Decimal(payload.amount)
    payment, created = await crud.create_payment_if_not_exists(db, transaction_id=payload.transaction_id, user_id=user.id, account_id=account.id, amount=amount)

    return {"status": "ok", "created": created, "payment_id": payment.id}