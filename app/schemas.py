from pydantic import BaseModel, Field


class KLSchema(BaseModel):
    """Pydantic модель для создания записи в килл-лист"""
    phone: str = Field(description='Номер клиента')
    contact_person: str = Field(description='Результат звонка')

class ResultForDeleteSchema(BaseModel):
    """Pydantic модель для передачи в килл-лист статусов для ежедневной зачистки"""
    contact_person1: str = Field(description='Contact_person на ежедневное удаление из килл листа')
    contact_person2: str = Field(description='Contact_person на ежедневное удаление из килл листа')


class ReestrSchema(BaseModel):
    """Pydantic модель для создания записи в базу с реестом клиентов"""
    bnpl_phone: str = Field(description='Номер клиента')
    debt: str = Field(description='Сумма долга')
    max_dpd: str = Field(description='Просрочка')
    id: str = Field(description='Что-то непонятное')
    call_date: str = Field(description='Дата звонка')


class CallInfoResponseSchema(BaseModel):
    """Pydantic модель для ответа"""
    detail: str = Field(default='created')
