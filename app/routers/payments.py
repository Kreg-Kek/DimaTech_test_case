from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app import schemas, crud
from app.database import get_session

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=schemas.PaymentRead, status_code=status.HTTP_201_CREATED)
async def create_payment(payment_in: schemas.PaymentCreate, db: AsyncSession = Depends(get_session)):
    try:
        payment = await crud.create_payment_and_apply(db, payment_in)
        await db.commit()
        return payment
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Payment with this uid already exists")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))