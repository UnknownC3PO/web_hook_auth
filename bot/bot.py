import logging
import db
import config
import messages
import buttons

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from bot.settings import (BOT_TOKEN, HEROKU_APP_NAME,
                          WEBHOOK_URL, WEBHOOK_PATH,
                          WEBAPP_HOST, WEBAPP_PORT)
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    db.reg_user(message.chat.id, None)
    await Form.name.set()
    await message.reply(messages.auth_msg[0])


@dp.message_handler(commands='name_update')
async def name_update(message: types.Message):
    db.change_data(message.chat.id, message.text)
    await message.reply(messages.changed_msg[0])


@dp.message_handler(commands='age_update')
async def age_update(message):
    db.change_data(message.chat.id, message.text)
    await message.reply(messages.changed_msg[1])


@dp.message_handler(commands='sex_update')
async def age_update(message):
    db.change_data(message.chat.id, message.text)
    await message.reply(messages.changed_msg[2])


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply(messages.cancel[0], reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    db.reg_user(message.chat.id, message.text)
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply(messages.auth_msg[1], reply_markup=buttons.process_name_back())


@dp.message_handler(state='*', commands='BackToName')
async def process_age(message: types.Message):
    markup = types.ReplyKeyboardRemove()
    await Form.name.set()
    await message.reply(messages.auth_msg[0], reply_markup=markup)


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    return await message.reply(messages.wrong_msg[0])


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    db.reg_user(message.chat.id, message.text)
    await Form.next()
    await state.update_data(age=int(message.text))

    await message.reply(messages.auth_msg[2], reply_markup=buttons.process_age())


@dp.message_handler(state='*', commands='BackToAge')
async def process_age(message: types.Message):
    await Form.age.set()
    await message.reply(messages.auth_msg[1], reply_markup=buttons.process_name_back())


@dp.message_handler(lambda message: message.text not in ["Male", "Female", "Other"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply(messages.wrong_msg[1])


@dp.message_handler(lambda message: message.text)
async def answet_from_buttons(message: types.message):
    if message.text == '<About>':
        await bot.send_message(message.chat.id, messages.register[0])
    elif message.text == '<Settings>':
        await bot.send_message(message.chat.id, messages.settings[0], reply_markup=buttons.settings())
    elif message.text == '<Change_name>':
        await bot.send_message(message.chat.id, messages.change_help[0])
    elif message.text == '<Change_age>':
        await bot.send_message(message.chat.id, messages.change_help[1])
    elif message.text == '<Change_gender>':
        await bot.send_message(message.chat.id, messages.change_help[2])
    elif message.text == '<Back>':
        await bot.send_message(message.chat.id, messages.select[0], reply_markup=buttons.back())
    elif message.text == '<Exit>':
        markup = types.ReplyKeyboardRemove(selective=False)
        await bot.send_message(message.chat.id, messages.exit_from_menu[0], reply_markup=markup)


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        db.reg_user(message.chat.id, message.text)
        data['gender'] = message.text
        markup_inline = types.InlineKeyboardMarkup()
        main_menu = types.InlineKeyboardButton(text='menu', callback_data='menu')
        markup_inline.add(main_menu)
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Hi! Nice to meet you,', md.bold(data['name'])),
                md.text('Age:', md.code(data['age'])),
                md.text('Gender:', data['gender']),
                sep='\n',
            ),
            reply_markup=buttons.enter_to_menu(),
            parse_mode=ParseMode.MARKDOWN,
        )

    await state.finish()


@dp.callback_query_handler(text="menu")
async def menu(call: types.CallbackQuery):
    await call.message.answer(messages.select[0], reply_markup=buttons.menu_buttons())



async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


async def on_shutdown(dp):
    logging.warning('Bye! Shutting down webhook connection')


def main():
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
