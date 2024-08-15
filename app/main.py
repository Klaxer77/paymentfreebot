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
from app.notification.router import router as notification_router
from app.users.auth import create_access_token
from app.users.dao import UsersDAO
from app.users.router import router as users_router
from app.users.schemas import SCreateToken, SToken
from app.utils.mock import mock_script
from app.logger import logger
from app.exceptions.users.exceptions import UserNotFound

app = FastAPI()

app.include_router(users_router)
app.include_router(payment_router)
app.include_router(transaction_router)
app.include_router(rating_router)
app.include_router(notification_router)


origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://twabot.netlify.app"
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
