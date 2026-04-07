import logging
import traceback

from datetime import datetime as dt
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import KLInfo, Reestr
from app.schemas import KLSchema, ReestrSchema, ResultForDeleteSchema



async def add_in_kl(
    async_session: AsyncSession,
    call_info_data: KLSchema,
):
    """Записать клиента в килл лист."""

    try:
        stmt = KLInfo(**call_info_data.model_dump(mode='python'))
        async_session.add(stmt)
        await async_session.commit()
        return True
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return False

async def check_number_kl(
    async_session: AsyncSession,
    number: str
):
    """Получить запись из килл листа по number."""
    try:
        stmt = select(KLInfo).where(KLInfo.phone == number)
        db_response = await async_session.execute(stmt)
        call_info = db_response.scalars().first()  # Получаем первую запись или None
        return call_info
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return False


async def add_in_clients_list(
    async_session: AsyncSession,
    call_info_data: ReestrSchema,
):
    """Записать клиента в колл лист."""

    try:
        stmt = Reestr(**call_info_data.model_dump(mode='python'))
        async_session.add(stmt)
        await async_session.commit()
        return True
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return False


async def get_kill_list(
        async_session: AsyncSession,
        limit: int = 1000
):
    """Поулчаем записи в килл листе по лимиту. Дефолтный 1000 записей."""
    try:
        stmt = select(KLInfo).limit(limit)
        db_reponse = await async_session.execute(stmt)
        calls_info = db_reponse.scalars().all()
        return calls_info
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return False
    
async def get_client_list(
        async_session: AsyncSession,
        limit: int = 1000
):
    """Поулчаем записи в реестре по лимиту. Дефолтный 1000 записей."""
    try:
        stmt = select(Reestr).limit(limit)
        db_reponse = await async_session.execute(stmt)
        clients = db_reponse.scalars().all()
        return clients
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return False

async def get_client(
        async_session: AsyncSession,
        number: str
):
    """Вытягиваем данные клиента по номеру"""
    try:
        stmt = select(Reestr).where(Reestr.bnpl_phone == number)  
        db_response = await async_session.execute(stmt)
        client = db_response.scalars().first()  
        return client
    except Exception as e:
        logging.warning(str(traceback.format_exc()))
        return False



async def clear_data(async_session: AsyncSession):
    """Полная очистка БД."""

    await async_session.execute(delete(KLInfo))
    await async_session.execute(delete(Reestr))
    await async_session.commit()
    logging.warning(f'На dimatech_web все БД очищенны')

async def clear_3F(async_session: AsyncSession, person:ResultForDeleteSchema):
    """Зачистка всех третьих лиц из килл листа и ежедневная очистка реестра"""
    await async_session.execute(delete(KLInfo).where(KLInfo.contact_person == person.contact_person1))
    await async_session.execute(delete(KLInfo).where(KLInfo.contact_person == person.contact_person2))
    await async_session.execute(delete(Reestr))
    await async_session.commit()
    logging.warning('На dimatech_web успешная ежедневная очистка реестра')

async def clear_only_person_from_KL(async_session: AsyncSession, person:ResultForDeleteSchema):
    """Зачистка только килл листа по контакт персон"""
    await async_session.execute(delete(KLInfo).where(KLInfo.contact_person == person.contact_person1))
    await async_session.execute(delete(KLInfo).where(KLInfo.contact_person == person.contact_person2))
    await async_session.commit()
    logging.warning('На dimatech_web успешная очистка конкретного cantact_person из килл-листа')

async def clear_only_reestr(async_session: AsyncSession):
    """Полная очистка только реестра."""
    await async_session.execute(delete(Reestr))
    await async_session.commit()
    logging.warning(f'На dimatech_web очищен только реестр')

async def clear_only_kill_list(async_session: AsyncSession):
    """Полная очистка только килл-листа."""
    await async_session.execute(delete(KLInfo))
    await async_session.commit()
    logging.warning(f'На dimatech_web очищен только килл-лист')