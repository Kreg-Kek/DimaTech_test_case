from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession

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

# --- users/admin helpers ---
async def get_user_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(models.User).where(models.User.email == email))
    return q.scalars().first()

async def create_user(db: AsyncSession, user_in: schemas.UserCreate):
    user = models.User(email=user_in.email, full_name=user_in.full_name, password_hash=user_in.password, is_admin=False)
    # password_hash should be already hashed by caller
    db.add(user)
    await db.flush()
    return user

async def update_user(db: AsyncSession, user_id: int, **fields):
    q = await db.execute(select(models.User).where(models.User.id == user_id))
    user = q.scalars().first()
    if not user:
        return None
    for k, v in fields.items():
        setattr(user, k, v)
    db.add(user)
    await db.flush()
    return user

async def delete_user(db: AsyncSession, user_id: int):
    q = await db.execute(select(models.User).where(models.User.id == user_id))
    user = q.scalars().first()
    if not user:
        return False
    await db.delete(user)
    await db.flush()
    return True

async def list_users(db: AsyncSession, limit: int=100, offset: int=0):
    q = await db.execute(select(models.User).limit(limit).offset(offset))
    return q.scalars().all()

# accounts/payments by user
async def get_accounts_by_user(db: AsyncSession, user_id: int):
    q = await db.execute(select(models.Account).where(models.Account.user_id == user_id))
    return q.scalars().all()

async def get_payments_by_user(db: AsyncSession, user_id: int):
    q = await db.execute(
        select(models.Payment).join(models.Account).where(models.Account.user_id == user_id)
    )
    return q.scalars().all()

# authentication helper: check credentials
async def authenticate_user(db: AsyncSession, email: str, plain_password: str, verify_fn):
    user = await get_user_by_email(db, email)
    if not user:
        # try admin table
        q = await db.execute(select(models.Admin).where(models.Admin.email == email))
        admin = q.scalars().first()
        if not admin:
            return None
        if verify_fn(plain_password, admin.password_hash):
            return {"type": "admin", "obj": admin}
        return None
    if verify_fn(plain_password, user.password_hash):
        return {"type": "user", "obj": user}
    return None

# helper to get accounts with balances for many users (admin requirement)
async def get_accounts_for_users(db: AsyncSession, user_ids: list[int]):
    q = await db.execute(select(models.Account).where(models.Account.user_id.in_(user_ids)))
    return q.scalars().all()