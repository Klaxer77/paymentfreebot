from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import Response
import httpx

from app.config import settings
from app.users.auth import create_access_token, register, send_event_to_subscribers
from app.users.schemas import SUserRegisterANDlogin

bot = Bot(token=settings.BOT_SECRET_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    async with httpx.AsyncClient() as ac:
        new_user = await register(
            user_data=SUserRegisterANDlogin(
                chat_id=message.chat.id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                username=message.from_user.username,
                is_premium=message.from_user.is_premium,
            )
        )
        token = create_access_token(new_user.chat_id)
        
        # await send_event_to_subscribers(data=token, event="GET TOKEN")

        button = InlineKeyboardButton(
            text="Открыть веб-приложение",
            web_app=types.WebAppInfo(url=f"{settings.WEB_APP_URL}/chat-id/{new_user.chat_id}"),
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

        await message.answer(
            f"Привет, {message.from_user.full_name}! Нажмите на кнопку ниже, чтобы открыть веб-приложение:",
            reply_markup=keyboard,
        )


@dp.message(Command("help"))
async def help(message: types.Message):
    await message.answer("/start - запустить бота\n" "/help - все доступные команды\n")
