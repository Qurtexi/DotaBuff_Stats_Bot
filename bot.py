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
    chat_id = message.from_user.id
    await bot.send_message(chat_id, "Hi!\nI'm DotaBuff Stats Bot!\nPowered by Qurtexi.")


# обработчик команды help
@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    chat_id = message.from_user.id
    await bot.send_message(chat_id, text('With this bot, you can view the statistics of your dotabuff profile.',
                                         'Commands you can use:',
                                         '/addprofile',
                                         '/deleteprofile',
                                         '/stats',
                                         sep='\n'))


@dp.message_handler(commands=['addprofile'])
async def add_profile(message: types.Message):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = message.from_user.id
    elements = session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).all()
    if len(elements) == 0:
        await Form.dotabuff.set()
        await bot.send_message(chat_id, 'Enter a link to your dotabuff account.')
    else:
        await bot.send_message(chat_id, 'Your profile is available in the database. Delete it, and then try again.')
        session.close()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    chat_id = message.from_user.id

    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await bot.send_message(chat_id, 'Canceled')


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
    await bot.send_message(chat_id, 'Your profile was successfully added.')


@dp.message_handler(commands='deleteprofile')
async def delete_handler(message: types.Message):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = str(message.from_user.id)
    elements = session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).all()
    if len(elements) != 0:
        session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).delete()
        session.commit()
        session.close()
        await bot.send_message(chat_id, 'Your profile was successfully deleted.')

    if len(elements) == 0:
        session.close()
        await bot.send_message(chat_id, "The linked profile was not detected.")


@dp.message_handler(commands=['stats'])
async def stats_info(message: types.Message):
    Session = sessionmaker(bind=engine)
    session = Session()
    chat_id = message.from_user.id
    elements = session.query(Dotabaff_db).filter(Dotabaff_db.chat_id == chat_id).first()
    url = elements.dotabuff
    result = parse(url)
    await bot.send_message(chat_id, text('Profile name: ' + result['player_name'],
                                         'Last match: ' + result['last_match'],
                                         'Wins: ' + result['wins'],
                                         'Losses: ' + result['losses'],
                                         'Abandons: ' + result['abandons'],
                                         'Win ratio: ' + result['win_rate'],
                                         sep='\n'
                                         ))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
