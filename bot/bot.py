import logging
import db
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


class Change(StatesGroup):
    change_name = State()
    change_age = State()
    change_gender = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    db.reg_user(message.chat.id, None)
    await Form.name.set()
    await message.reply(messages.auth_msg[0])


@dp.message_handler(state=[Change.change_name, Change.change_age, Change.change_gender])
async def age_update(message: types.Message, state: FSMContext):
    if message.text != 'Back to menu':
        k = await state.get_state()
        if db.change_data(message.chat.id, message.text, k):
            await message.reply(messages.changed_msg[0], reply_markup=buttons.menu_buttons())
            await state.finish()
        else:
            await message.reply(messages.error_data[0])
    else:
        await bot.send_message(message.chat.id, messages.select[0], reply_markup=buttons.menu_buttons())
        await state.finish()


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
    if db.check_value(message.text):
        db.reg_user(message.chat.id, message.text)
        async with state.proxy() as data:
            data['name'] = message.text
        await Form.next()
        await message.reply(messages.auth_msg[1], reply_markup=buttons.process_name_back())
    else:
        await message.reply(messages.error_data[1])


@dp.message_handler(lambda message: message.text in ['Back'], state='*')
async def process_age(message: types.Message, state: FSMContext):
    if await state.get_state() == 'Form:age':
        await Form.name.set()
        await message.reply(messages.auth_msg[0], reply_markup=buttons.process_name_back())
    elif await state.get_state() == 'Form:gender':
        await Form.age.set()
        await message.reply(messages.auth_msg[1], reply_markup=buttons.process_name_back())


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    return await message.reply(messages.wrong_msg[0])


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    if db.reg_user(message.chat.id, message.text):
        await Form.next()
        await state.update_data(age=int(message.text))
        await message.reply(messages.auth_msg[2], reply_markup=buttons.process_age())
    else:
        await message.reply(messages.wrong_msg[0])


@dp.message_handler(lambda message: message.text not in ["Male", "Female", "Other"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply(messages.wrong_msg[1])


@dp.message_handler(lambda message: message.text)
async def answet_from_buttons(message: types.message):
    if message.text == 'About':
        await bot.send_message(message.chat.id, db.about_user(message.chat.id))
    elif message.text == 'Settings':
        await bot.send_message(message.chat.id, messages.settings[0], reply_markup=buttons.settings())
    elif message.text == 'Change name':
        await Change.change_name.set()
        await bot.send_message(message.chat.id, messages.change_help[0], reply_markup=buttons.back_menu())
    elif message.text == 'Change age':
        await Change.change_age.set()
        await bot.send_message(message.chat.id, messages.change_help[0], reply_markup=buttons.back_menu())
    elif message.text == 'Change sex':
        await Change.change_gender.set()
        await bot.send_message(message.chat.id, messages.change_help[0], reply_markup=buttons.gender_back_menu())
    elif message.text == 'Back':
        await bot.send_message(message.chat.id, messages.select[0], reply_markup=buttons.back())
    elif message.text == 'Exit':
        markup = types.ReplyKeyboardRemove(selective=False)
        await bot.send_message(message.chat.id, messages.exit_from_menu[0], reply_markup=markup)


@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        db.reg_user(message.chat.id, message.text)
        data['gender'] = message.text
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Hi! Nice to meet you,', md.bold(data['name'])),
                md.text('Age:', md.code(data['age'])),
                md.text('Gender:', data['gender']),
                sep='\n',
            ),
            reply_markup=buttons.menu_buttons(),
            parse_mode=ParseMode.MARKDOWN,
        )

    await state.finish()


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
