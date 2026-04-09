from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app import models, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from .security import hash_password

async def create_user(db: AsyncSession, user_in: schemas.UserCreate):
    user = models.User(email=user_in.email, full_name=user_in.full_name)
    db.add(user)
    await db.flush()
    return user

async def get_user(db: AsyncSession, user_id: int):
    q = await db.execute(select(models.User).where(models.User.id == user_id))
    return q.scalars().first()

async def create_admin(db: AsyncSession, admin_in: schemas.AdminCreate):
    admin = models.Admin(email=admin_in.email, full_name=admin_in.full_name)
    db.add(admin)
    await db.flush()
    return admin

async def create_account(db: AsyncSession, account_in: schemas.AccountCreate):
    account = models.Account(user_id=account_in.user_id, balance=Decimal("0.00"))
    db.add(account)
    await db.flush()
    return account

async def get_account(db: AsyncSession, account_id: int):
    q = await db.execute(select(models.Account).where(models.Account.id == account_id))
    return q.scalars().first()

async def create_payment_and_apply(db: AsyncSession, payment_in: schemas.PaymentCreate):
    payment = models.Payment(uid=payment_in.uid, account_id=payment_in.account_id, amount=payment_in.amount)
    db.add(payment)
    try:
        await db.flush()
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

async def get_user_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(models.User).where(models.User.email == email))
    return q.scalars().first()

async def create_user(db: AsyncSession, user_in: schemas.UserCreate):
    user = models.User(email=user_in.email, full_name=user_in.full_name, password_hash=user_in.password, is_admin=False)
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

async def get_accounts_by_user(db: AsyncSession, user_id: int):
    q = await db.execute(select(models.Account).where(models.Account.user_id == user_id))
    return q.scalars().all()

async def get_payments_by_user(db: AsyncSession, user_id: int):
    q = await db.execute(
        select(models.Payment).join(models.Account).where(models.Account.user_id == user_id)
    )
    return q.scalars().all()

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

async def get_accounts_for_users(db: AsyncSession, user_ids: list[int]):
    q = await db.execute(select(models.Account).where(models.Account.user_id.in_(user_ids)))
    return q.scalars().all()

async def get_or_create_account(db: AsyncSession, owner_id: int, account_id: int | None = None):
    if account_id is not None:
        q = await db.execute(select(models.Account).where(models.Account.id == account_id, models.Account.user_id == owner_id))
        acc = q.scalars().first()
        if acc:
            return acc

    acc = models.Account(user_id=owner_id, balance=Decimal("0.00"))
    db.add(acc)
    await db.flush()
    return acc

async def create_payment_if_not_exists(db: AsyncSession, transaction_id: str, user_id: int, account_id: int, amount: Decimal):
    q = await db.execute(select(models.Payment).where(models.Payment.uid == transaction_id))
    existing = q.scalars().first()
    if existing:
        return existing, False

    q2 = await db.execute(select(models.Account).where(models.Account.id == account_id, models.Account.user_id == user_id).with_for_update())
    acc = q2.scalars().first()
    if acc is None:
        acc = models.Account(user_id=user_id, balance=Decimal("0.00"))
        db.add(acc)
        await db.flush()

    payment = models.Payment(uid=transaction_id, account_id=acc.id, amount=Decimal(amount))
    db.add(payment)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        q3 = await db.execute(select(models.Payment).where(models.Payment.uid == transaction_id))
        existing = q3.scalars().first()
        if existing:
            return existing, False
        raise

    acc.balance = (acc.balance or Decimal("0.00")) + Decimal(amount)
    db.add(acc)

    await db.commit()
    await db.refresh(payment)
    await db.refresh(acc)
    return payment, True

async def create_test_entities(db: AsyncSession):
    q = await db.execute(select(models.User).where(models.User.email == "test_user@example.com"))
    user = q.scalars().first()
    if not user:
        user = models.User(
            email="test_user@example.com",
            full_name="Иван Иваныч",
            password_hash=hash_password("123"),
            is_admin=False,
        )
        db.add(user)
        await db.flush()

    # тестовый юзер
    q = await db.execute(select(models.Account).where(models.Account.user_id == user.id))
    account = q.scalars().first()
    if not account:
        account = models.Account(user_id=user.id, balance=Decimal("5000.00"))
        db.add(account)
        await db.flush()

    # тестовый админ
    q = await db.execute(select(models.User).where(models.User.email == "test_admin@example.com"))
    admin = q.scalars().first()
    if not admin:
        admin = models.User(
            email="test_admin@example.com",
            full_name="Админ Дима",
            password_hash=hash_password("456"), 
            is_admin=True,
        )
        db.add(admin)
        await db.flush()

    await db.commit()
    await db.refresh(user)
    await db.refresh(account)
    await db.refresh(admin)
    return {"user_id": user.id, "account_id": account.id, "admin_id": admin.id}