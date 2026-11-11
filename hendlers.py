from aiogram import Router 
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from db import engine
from models import Users
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



router = Router()

class ResultState(StatesGroup):
    waiting_for_score = State()

async def user_in_rating(user_answer):
    sesion = AsyncSession(bind=engine,expire_on_commit=False)
    try:
        query = select(Users.amount)
        result = await sesion.execute(query)
        amounts = result.scalars().all()

        amounts = sorted(amounts, reverse=True)

        rate = amounts.index(int(user_answer))+1
        
        return rate
    finally:
        await sesion.close()


@router.message(CommandStart())
async def start_message(message : Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Загрузить результат", callback_data="upload_result")],
            [InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
            [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
        ]
    )


    sesion = AsyncSession(bind = engine,expire_on_commit=False)

    try:
        query = select(Users).where(Users.tg_id == message.from_user.id)
        result = await sesion.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            user = Users(
                tg_id = message.from_user.id,
                username = message.from_user.username,
                first_name = message.from_user.first_name,
                last_name = message.from_user.last_name,
                amount = 0
            )
            sesion.add(user)
            await sesion.commit()
            await message.answer(
                "<b><u>🥊 ROCKY BOXER</u></b>\n\n"
                f"Приветствуем {message.from_user.first_name} в боте силомера ROCKY BOXER!\n\n"
                "💥 Загружай свой результат\n"
                "🏆 Следи за своим местом в рейтинге\n"
                "🎁 Побеждай и получай призы от наших партнёров\n\n"
                "Готов проверить свою силу и побороться за первое место?\n\n"
                "Жми кнопку ниже и начинай! 👇",
                reply_markup=keyboard
                )

        else:
            await message.answer(
                "<b><u>🥊 ROCKY BOXER</u></b>\n\n"
                f"С возращением {message.from_user.first_name} в боте силомера ROCKY BOXER!\n\n"
                "💥 Загружай свой результат\n"
                "🏆 Следи за своим местом в рейтинге\n"
                "🎁 Побеждай и получай призы от наших партнёров\n\n"
                "Готов проверить свою силу и побороться за первое место?\n\n"
                "Жми кнопку ниже и начинай! 👇",
                reply_markup=keyboard
            )
    finally:
       await sesion.close()



@router.callback_query(lambda callback:  callback.data == "upload_result")
async def upload_result(callback: CallbackQuery,state: FSMContext):
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📸 Загрузить результат", callback_data="upload_result")],
                [InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
                [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
            ]
    )

    sesion = AsyncSession(bind = engine,expire_on_commit=False)

    try:
        query = select(Users).where(Users.tg_id==callback.from_user.id)
        result = await sesion.execute(query)
        user = result.scalar_one_or_none()


        await callback.answer()
        
        if user:
            await callback.message.answer("Введи свой результат (число очков), который ты выбил на автомате. Отправь его мне одним сообщением.")
            await state.set_state(ResultState.waiting_for_score) # включаю режим ожидания
        else:
            await callback.message.answer("Сначала введите /start, чтобы зарегистрироваться!",reply_markup=keyboard)
    finally:

        await sesion.close()






@router.message(ResultState.waiting_for_score)
async def save_result(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Загрузить результат", callback_data="upload_result")],
            [InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
            [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
        ]
    )

    user_answer = message.text

    if user_answer and user_answer.isdigit():
        sesion = AsyncSession(bind=engine, expire_on_commit=False)
        try:
            query = select(Users).where(Users.tg_id == message.from_user.id)
            result = await sesion.execute(query)
            user = result.scalar_one_or_none()

            if user:
                user.amount = int(user_answer)
                await sesion.commit()

                await state.clear()  #выключаю режим ожидания

                await message.answer(
                    "<b><u>✅ Результат засчитан!</u></b>\n\n"
                    f"Твой удар: {user_answer}\n\n"
                    f"Ты на {await user_in_rating(user_answer)}-м месте в рейтинге.\n"
                    "Бей ещё! 🥊\n\n"
                    "Готов проверить свою силу еще раз?\n\n"
                    "Жми кнопку ниже и продолжай! 👇",
                    reply_markup=keyboard
                )
        finally:
            await sesion.close()
    else:
        await message.answer("Пожалуйста, введи число (например: 845)")






@router.callback_query(lambda callback:  callback.data == "leaderboard")
async def leaderboard(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📸 Загрузить результат", callback_data="upload_result")],
                [InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
                [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
            ]
    )

    sesion = AsyncSession(bind = engine,expire_on_commit=False)

    try:
        query = select(Users).order_by(Users.amount.desc()).limit(10)
        result = await sesion.execute(query)
        top_users = result.scalars().all()

        text_lines=["🏆 Таблица лидеров, топ-10\n"]
        index=1
        for user in top_users:
            name = f"@{user.username}" if user.username else f"Пользователь:{user.tg_id}"
            text_lines.append(f"{index}. {name} - {user.amount} очков")
            index+=1

        finel_text = "\n".join(text_lines) 

        await callback.answer()
        await callback.message.answer(finel_text,reply_markup=keyboard)

    finally:

        await sesion.close()

    




@router.callback_query(lambda callback:  callback.data == "my_profile")
async def my_profile(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📸 Загрузить результат", callback_data="upload_result")],
                [InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
                [InlineKeyboardButton(text="👤 Мой профиль", callback_data="my_profile")]
            ]
    )

    sesion = AsyncSession(bind = engine,expire_on_commit=False)

    try:
        query = select(Users).where(Users.tg_id==callback.from_user.id)
        result = await sesion.execute(query)
        user = result.scalar_one_or_none()

        await callback.answer()

        if user:
            await callback.message.answer("👤 Мой профиль \n"
                           f"тг: @{user.username} \n"
                           f"Результат: {user.amount} \n"
                           f"Текущее место: {await user_in_rating(user.amount)}-е",
                           reply_markup=keyboard
                           )
        else:
            await callback.message.answer("Сначала введите /start, чтобы зарегистрироваться!",reply_markup=keyboard)

    finally:

        await sesion.close()