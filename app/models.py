from sqlalchemy import Column, String, Integer, DateTime, func
from app.database import Base

class KLInfo(Base):
    """Base table."""

    __tablename__ = "kill_list"

    id = Column(Integer, primary_key=True)
    phone = Column(String)
    contact_person = Column(String)
    created_at = Column(DateTime, default=func.now())
    


class Reestr(Base):
    """Base table."""

    __tablename__ = "client_list"

    id_sys = Column(Integer, primary_key=True)
    bnpl_phone = Column(String)
    debt = Column(String)
    max_dpd = Column(String)
    id = Column(String)
    call_date = Column(String)

