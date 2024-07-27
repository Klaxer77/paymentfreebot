from fastapi import FastAPI
from aiogram import types, Dispatcher, Bot
from app.bot import dp, bot
from app.config import settings
from app.users.router import router as users_router


app = FastAPI()

app.include_router(users_router)

WEBHOOK_PATH = f"/bot/{settings.BOT_SECRET_TOKEN}"
WEBHOOK_URL = f"{settings.NGROK_TUNNEL_URL}{WEBHOOK_PATH}"


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp._process_update(bot,telegram_update)
    

@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL
        )

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()