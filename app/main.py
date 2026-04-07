import asyncio
import logging
import traceback
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.encoders import jsonable_encoder
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud
from app.async_log import init_logger
from app.schemas import KLSchema, CallInfoResponseSchema, ReestrSchema, ResultForDeleteSchema
from app.database import get_session, create_database
from os import getenv
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN=getenv('ACCESS_TOKEN')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Параметры приложения."""
    asyncio.create_task(init_logger())
    await create_database()
    yield


app = FastAPI(
    lifespan=lifespan,
    title='DimaTech_web',
    version='1.0.1',
)


api_key = APIKeyHeader(name='Authorization')


def check_web_key(authorization: str = Depends(api_key)):
    """Проверка ключа api для openapi"""

    if not authorization or str(authorization) != ACCESS_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Unauthorized')
    return True


@app.post("/add_in_kl/",
          response_model=CallInfoResponseSchema,
          status_code=status.HTTP_201_CREATED)
async def create_call_record(
    call_info: KLSchema,
    authorization: str = Depends(check_web_key),
    async_session: AsyncSession = Depends(get_session)
):
    try:
        created = await crud.add_in_kl(
            async_session, call_info
        )
        if not created:
            return JSONResponse(content={'detail': 'client do not banned'},
                                status_code=status.HTTP_400_BAD_REQUEST)
        return JSONResponse(content={'detail': 'success'},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return JSONResponse(
            content={'detail': 'server error'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@app.get("/get_kill_list/",
         response_model=CallInfoResponseSchema,
         status_code=status.HTTP_200_OK)
async def get_kill_list(
    limit: int = 1000,
    authorization: str = Depends(check_web_key),
    async_session: AsyncSession = Depends(get_session)
):
    try:
        calls_info = await crud.get_kill_list(
            async_session,
            limit=limit
        )
        if not calls_info:
            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT
            )
        return JSONResponse(content=jsonable_encoder(calls_info),
                            status_code=status.HTTP_200_OK)
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return JSONResponse(
            content={'detail': 'server error'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.get("/check_kill/", response_model=bool)
async def check_kill_endpoint(
    number: str,
    authorization: str = Depends(check_web_key),
    async_session: AsyncSession = Depends(get_session)
):
    """Эндпоинт для проверки наличия number в базе данных."""
    try:
        exists = await crud.check_number_kl(async_session, number)
        return exists is not None  # Возвращаем True, если запись найдена, иначе False
    except Exception:
        logging.warning(str(traceback.format_exc()))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")


@app.post("/add_in_client_list/",
          response_model=CallInfoResponseSchema,
          status_code=status.HTTP_201_CREATED)
async def create_call_list(
    call_info: ReestrSchema,
    authorization: str = Depends(check_web_key),
    async_session: AsyncSession = Depends(get_session)
):
    try:
        created = await crud.add_in_clients_list(
            async_session, call_info
        )
        if not created:
            return JSONResponse(content={'detail': 'client do not write'},
                                status_code=status.HTTP_400_BAD_REQUEST)
        return JSONResponse(content={'detail': 'success'},
                            status_code=status.HTTP_201_CREATED)
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return JSONResponse(
            content={'detail': 'server error'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.get("/get_client_list/",
         response_model=CallInfoResponseSchema,
         status_code=status.HTTP_200_OK)
async def get_client_list(
    limit: int = 1000,
    authorization: str = Depends(check_web_key),
    async_session: AsyncSession = Depends(get_session)
):
    try:
        clients = await crud.get_client_list(
            async_session,
            limit=limit
        )
        if not clients:
            return JSONResponse(
                status_code=status.HTTP_204_NO_CONTENT
            )
        return JSONResponse(content=jsonable_encoder(clients),
                            status_code=status.HTTP_200_OK)
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return JSONResponse(
            content={'detail': 'server error'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.get("/get_client/",
         response_model=str,
         status_code=status.HTTP_200_OK)
async def get_client_info(
    number: str,
    authorization: str = Depends(check_web_key),
    async_session: AsyncSession = Depends(get_session)
):
    try:
        calls_info = await crud.get_client(
            async_session,
            number=number
        )
        if not calls_info:
            # return JSONResponse(
            #     status_code=status.HTTP_204_NO_CONTENT
            # )
            return 'not_found'
        return JSONResponse(content=jsonable_encoder(calls_info),
                            status_code=status.HTTP_200_OK)
    except Exception:
        logging.warning(str(traceback.format_exc()))
        return JSONResponse(
            content={'detail': 'server error'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.delete("/clear_all/", response_model=dict)
async def clear_database(
    authorization: str = Depends(check_web_key), 
    async_session: AsyncSession = Depends(get_session)):
    """Эндпоинт для очистки базы данных."""
    try:
        await crud.clear_data(async_session)
        return {"message": "База данных успешно очищена."}
    except Exception as e:
        logging.warning(str(traceback.format_exc()))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_3F/", response_model=dict)
async def clear_3F_from_kl(
    result: ResultForDeleteSchema,
    authorization: str = Depends(check_web_key), 
    async_session: AsyncSession = Depends(get_session)):
    """Эндпоинт для ежедневной очистки реестра и третьих лиц из килл-листа."""
    try:
        await crud.clear_3F(async_session, result)
        return {"message": "База данных успешно очищена."}
    except Exception as e:
        logging.warning(str(traceback.format_exc()))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_only_person_from_KL/", response_model=dict)
async def clear_only_person_from_KL(
    result: ResultForDeleteSchema,
    authorization: str = Depends(check_web_key), 
    async_session: AsyncSession = Depends(get_session)):
    """Эндпоинт для очистки только конкретных лиц из килл-листа."""
    try:
        await crud.clear_only_person_from_KL(async_session, result)
        return {"message": "Килл-лист успешно очищен от конкретных лиц."}
    except Exception as e:
        logging.warning(str(traceback.format_exc()))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear_only_reestr/", response_model=dict)
async def clear_only_reestr(
    authorization: str = Depends(check_web_key), 
    async_session: AsyncSession = Depends(get_session)):
    """Эндпоинт для очистки только реестра."""
    try:
        await crud.clear_only_reestr(async_session)
        return {"message": "Реестр успешно очищен."}
    except Exception as e:
        logging.warning(str(traceback.format_exc()))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/clear_only_kill_list/", response_model=dict)
async def clear_only_kill_list(
    authorization: str = Depends(check_web_key), 
    async_session: AsyncSession = Depends(get_session)):
    """Эндпоинт для очистки только килл-листа."""
    try:
        await crud.clear_only_kill_list(async_session)
        return {"message": "База данных успешно очищена."}
    except Exception as e:
        logging.warning(str(traceback.format_exc()))
        raise HTTPException(status_code=500, detail=str(e))
