from aiogram import Router 
from aiogram.types import Message
from aiogram.filters import CommandStart
from db import engine
from models import Users

router = Router()

@router.message(CommandStart())
async def start_message(message : Message):
    await message.answer("hello from pidoras")



