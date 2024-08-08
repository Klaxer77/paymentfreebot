import time

from aiogram import types
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.bot import bot, dp
from app.config import settings
from app.exceptions.base import ServerError
from app.exceptions.schemas import SExceptionsINFO
from app.exceptions.users.exceptions import AccessTokenException
from app.payment.router import router as payment_router
from app.transaction.router import router as transaction_router
from app.rating.router import router as rating_router
from app.users.auth import create_access_token
from app.users.dao import UsersDAO
from app.users.router import router as users_router
from app.users.schemas import SCreateToken, SToken
from app.utils.mock import mock_script
from app.logger import logger
from app.exceptions.users.exceptions import UserNotFound

openapi_url = None
redoc_url = None

if settings.MODE != "PROD":
    openapi_url = "/openapi.json"
    redoc_url = "/redoc"

app = FastAPI(openapi_url=openapi_url, redoc_url=redoc_url)

app.include_router(users_router)
app.include_router(payment_router)
app.include_router(transaction_router)
app.include_router(rating_router)

origins = [
    "http://localhost:3000",
    settings.NGROK_TUNNEL_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", 
                   "Access-Control-Allow-Origin",
                   "Authorization"],
)

WEBHOOK_PATH = f"/bot/{settings.BOT_SECRET_TOKEN}"
WEBHOOK_URL = f"{settings.NGROK_TUNNEL_URL}{WEBHOOK_PATH}"


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    """

    `Only Webhook URL`

    """
    if not update:
        return None
    telegram_update = types.Update(**update)
    await dp._process_update(bot, telegram_update)


@app.get("/run-mock-script")
async def run_mock_script():
    """

    `Mock данные для тестов`

    """
    await mock_script()
    return {"message": "Successfully!!!"}


@app.post("/create/token")
async def create_token(response: Response, request: Request, user: SCreateToken) -> SToken | SExceptionsINFO:
    """
    **Создать токен для аутентификации пользователя**

    **Args**

    `chat_id` - id чата пользователя в telegram

    **Returns**

    Возвращает токен для аутентификации

    **Note**

    Пользователь должен быть зарегистрирован в боте с данным _chat_id_

    """
    origin = request.headers.get('origin')
    origin_list = ["http://localhost:3000","http://localhost:8000",settings.NGROK_TUNNEL_URL]
    if settings.MODE == "PROD":
        origin_list = [""] #TODO добавить свой список в проде
    if origin not in origin_list:
        raise AccessTokenException
    try:
        user = await UsersDAO.check_user(chat_id=user.chat_id)
        if not user:
            raise UserNotFound
        token = create_access_token(user.chat_id)
        response.set_cookie("token", token)
        logger.debug(token)
        return {"token": token}
    
    except UserNotFound as e:
        return {"detail": e.detail}
    except (SQLAlchemyError, Exception) as e:
        if isinstance(e, SQLAlchemyError):
            msg = "Database Exc"
        if isinstance(e, Exception):
            msg = "Unknown Exc"
        msg += ": cannot return token"
        logger.error(msg=msg, exc_info=True)
        raise ServerError


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(url=WEBHOOK_URL)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # При подключении Prometheus + Grafana подобный лог не требуется
    logger.info("Request handling time", extra={"process_time": round(process_time, 4)})
    return response
