from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import Response
import httpx

from app.config import settings
from app.users.auth import register
from app.users.schemas import SUserRegisterANDlogin

bot = Bot(token=settings.BOT_SECRET_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    
    webhook_url = settings.USER_WEBHOOK_URL
    async with httpx.AsyncClient() as client:
        await client.post(webhook_url, json={"chat_id": message.chat.id})

    await register(
        user_data=SUserRegisterANDlogin(
            chat_id=message.chat.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            is_premium=message.from_user.is_premium,
        )
    )

    button = InlineKeyboardButton(
        text="Открыть веб-приложение",
        web_app=types.WebAppInfo(url=f"{settings.WEB_APP_URL}"),
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(
        f"Привет, {message.from_user.full_name}! Нажмите на кнопку ниже, чтобы открыть веб-приложение:",
        reply_markup=keyboard,
    )


@dp.message(Command("help"))
async def help(message: types.Message):
    await message.answer("/start - запустить бота\n" "/help - все доступные команды\n")
