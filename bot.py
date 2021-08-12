import logging

import os

from cfg import *
from db_map import Base, Dotabaff_db
from parser import parse

from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import *
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import keyboard as kb

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

engine = create_engine('sqlite:///users.db')

if not os.path.isfile(f'/users.db'):
    Base.metadata.create_all(engine)


class Form(StatesGroup):
    dotabuff = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Hi!\nI'm DotaBuff Stats Bot!\nPowered by Qurtexi.",
                         reply_markup=kb.all_kb)


# обработчик команды help
@dp.message_handler(text="Help")
async def send_help(message: types.Message):
    await message.answer(text('With this bot, you can view the statistics of your dotabuff profile.',
                              'Commands you can use:',
                              '/addprofile',
                              '/deleteprofile',
                              '/stats',
                              sep='\n'), reply_markup=kb.all_kb)


@dp.message_handler(text="Add profile")
async def add_profile(message: types.Message):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = message.from_user.id
    elements = session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).all()

    if len(elements) == 0:
        await Form.dotabuff.set()
        await message.answer('Enter a link to your dotabuff account.', reply_markup=kb.cancel_kb)
    else:
        await message.answer('Your profile is available in the database. Delete it, and then try again.',
                             reply_markup=kb.all_kb)
        session.close()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='Cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer('Canceled', reply_markup=kb.all_kb)


@dp.message_handler(state=Form.dotabuff)
async def process_add(message: types.Message, state: FSMContext):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = str(message.from_user.id)
    NewElement = Dotabaff_db(chat_id=chat_id, dotabuff=message.text)
    session.add(NewElement)
    session.commit()
    session.close()
    await state.finish()
    await message.answer('Your profile was successfully added.', reply_markup=kb.all_kb)


@dp.message_handler(text='Delete profile')
async def delete_handler(message: types.Message):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = str(message.from_user.id)
    elements = session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).all()

    if len(elements) != 0:
        session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).delete()
        session.commit()
        session.close()
        await message.answer('Your profile was successfully deleted.', reply_markup=kb.all_kb)

    if len(elements) == 0:
        session.close()
        await message.answer("The linked profile was not detected.", reply_markup=kb.all_kb)


@dp.message_handler(text="Show statistic")
async def stats_info(message: types.Message):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = message.from_user.id
    elements = session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).first()
    url = elements.dotabuff
    result = parse(url)

    if elements is None:
        await message.answer('There is no profile in the database. Click on the "Add profile" button and add your '
                             'DotaBuff profile')
    else:
        if result is not None:
            if result == 1:
                await message.answer(text("An error has occurred. Please try again."), reply_markup=kb.all_kb)
            else:
                await message.answer(text('Profile name: ' + result['player_name'],
                                          'Last match: ' + result['last_match'],
                                          'Wins: ' + result['wins'],
                                          'Losses: ' + result['losses'],
                                          'Abandons: ' + result['abandons'],
                                          'Win ratio: ' + result['win_rate'],
                                          '____________________________________',
                                          result['ts_data_overview'],
                                          f"Total statistic: {result['profile-qual']}",
                                          f"{result['ts_recent_text']}: {result['ts_recent_score']}",
                                          f"{result['ts_total_text']}: {result['ts_total_score']}",
                                          f"{result['ts_plus_text']}: {result['ts_plus_score']}",

                                          sep='\n'
                                          ), reply_markup=kb.all_kb)
        else:
            await message.answer(text("You entered the wrong link. Please delete it and enter the link related to the "
                                      "player's profile on the site https://www.dotabuff.com/."),reply_markup=kb.all_kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
