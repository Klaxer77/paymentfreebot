import io
import uuid
from aiogram import Dispatcher, Bot, types
from aiogram.utils.web_app import WebAppUser
from aiogram.filters import Command
from fastapi import Response
from app.config import settings
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo, InlineKeyboardMarkup
from app.users.auth import create_access_token
from app.users.router import register
from app.users.schemas import SUserRegisterANDlogin

bot = Bot(token=settings.BOT_SECRET_TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start(message: types.Message):

    await register(user_data = SUserRegisterANDlogin(
        chat_id=message.chat.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
))
    token = create_access_token(message.chat.id)
    
    button = InlineKeyboardButton(
        text="Открыть веб-приложение", 
        web_app=types.WebAppInfo(url=f"{settings.WEB_APP_URL}?token={token}")
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await message.answer(f"Привет, {message.from_user.full_name}! Нажмите на кнопку ниже, чтобы открыть веб-приложение:", reply_markup=keyboard)
    
@dp.message(Command('help'))
async def help(message: types.Message):
    await message.answer(
        "/start - запустить бота\n"
        "/help - все доступные команды\n"
    )