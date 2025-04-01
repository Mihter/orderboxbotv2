from datetime import datetime

from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, message_id, CallbackQuery, InlineKeyboardButton, \
    InputFile, FSInputFile, InlineKeyboardMarkup, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from decimal import Decimal
import text
from datetime import datetime

from database.db import DataBase

import html
import logging


db = DataBase()
router = Router()


# Определение состояний
class OrderStates(StatesGroup):
    order_box = State()
    choosing_date = State()
    survey = State()


print("v1.0")


@router.message(Command("start"))
async def start_handler(message: Message):
    tg_id = message.from_user.id
    username = message.from_user.username
    db.save_user_action(tg_id, username, '/start')

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Ознакомиться с наполнением", callback_data="view_contents"))
    builder.row(InlineKeyboardButton(text="Хочу коробку", callback_data="order_box"))

    photo = FSInputFile("./img/VIP_Box.jpg")
    await message.answer_photo(photo, caption=text.privet, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'view_contents')
async def view_contents_handler(call: CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Хочу коробку", callback_data="order_box")
    )
    await call.message.answer(text=text.view_contents, reply_markup=builder.as_markup())
    await state.set_state(OrderStates.order_box)


@router.callback_query(F.data == 'order_box')
async def get_date_handler(call: CallbackQuery, state: FSMContext):
    tg_id = call.from_user.id
    username = call.from_user.username
    #тут событие 'want_box'
    db.save_user_action(tg_id, username, 'want_box')

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Закажу позже", callback_data="later_order"))
    await call.message.answer(text=text.pleace_date, reply_markup=builder.as_markup())
    await state.set_state(OrderStates.choosing_date)


@router.message(OrderStates.choosing_date)
async def save_dates_handler(message: Message, state: FSMContext):
    dates = message.text.strip()

    if not validate_dates(dates):
        await message.answer("Некорректный формат даты! Введите в формате ДД.ММ, например: 23.01 15.04 .\nОбязательно пробел между датами!")
        return

    await state.update_data(dates=dates)

    tg_id = message.from_user.id
    db.save_order_date(tg_id, dates)

    username = message.from_user.username
    db.save_user_action(tg_id, username, 'preorder')


    await message.answer("Ваши даты сохранены!\n Мы уведомим вас ближе к сроку.")
    await state.set_state(OrderStates.survey)
    await message.answer(text.answer_one)
    print(await state.get_state())


def validate_dates(dates: str) -> bool:
    date_list = dates.split(' ')
    for date_str in date_list:
        try:
            datetime.strptime(date_str, "%d.%m")  # Проверка корректности дня и месяца
        except ValueError:
            return False
    return True

@router.callback_query(F.data == 'later_order')
async def later_order_handler(call: CallbackQuery, state: FSMContext):
    tg_id = call.from_user.id
    username = call.from_user.username
    #тут метод по внесению инфы для метрик, событие 'later_order'
    db.save_user_action(tg_id, username, 'later_order')

    await call.message.answer("Окей, в другой раз.")
    await call.message.answer(text.answer_one)
    await state.set_state(OrderStates.survey)
    print(await state.get_state())

@router.message(OrderStates.survey)
async def save_answer_handler(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    username = message.from_user.username
    answer = message.text.strip()

    success = db.save_poll_answer(tg_id, answer)

    if success:
        await message.answer("Ваш ответ сохранен!")
        db.save_user_action(tg_id, username, 'survey')
        await state.clear()

        await start_handler(message)
    else:
        await message.answer("Вы уже проходили опрос и не можете изменить ответ.")
        await state.clear()
        await start_handler(message)