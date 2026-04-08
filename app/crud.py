from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app import models, schemas

async def create_user(db, user_in: schemas.UserCreate):
    user = models.User(email=user_in.email, full_name=user_in.full_name)
    db.add(user)
    await db.flush()
    return user

async def get_user(db, user_id: int):
    q = await db.execute(select(models.User).where(models.User.id == user_id))
    return q.scalars().first()

async def create_admin(db, admin_in: schemas.AdminCreate):
    admin = models.Admin(email=admin_in.email, full_name=admin_in.full_name)
    db.add(admin)
    await db.flush()
    return admin

async def create_account(db, account_in: schemas.AccountCreate):
    account = models.Account(user_id=account_in.user_id, balance=Decimal("0.00"))
    db.add(account)
    await db.flush()
    return account

async def get_account(db, account_id: int):
    q = await db.execute(select(models.Account).where(models.Account.id == account_id))
    return q.scalars().first()

async def create_payment_and_apply(db, payment_in: schemas.PaymentCreate):
    # Atomically create payment and update account balance
    payment = models.Payment(uid=payment_in.uid, account_id=payment_in.account_id, amount=payment_in.amount)
    db.add(payment)
    try:
        await db.flush()  # may raise IntegrityError on duplicate uid
    except IntegrityError:
        await db.rollback()
        raise

    q = await db.execute(select(models.Account).where(models.Account.id == payment_in.account_id).with_for_update())
    account = q.scalars().first()
    if account is None:
        raise ValueError("Account not found")
    account.balance += Decimal(payment_in.amount)
    db.add(account)
    await db.flush()
    return payment