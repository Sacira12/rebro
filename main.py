import asyncio
import functional_buy
import functional_man
import config
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

BOT_TOKEN = config.bot_token  # вставляем токен вашего бота
pin = config.pin
# Создаем объекты бота и диспетчера
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        'начинаем работу'
    )


@dp.message(Command(commands="help"))
async def help(message: Message):
    l = await functional_man.check_man("tg_id")
    if message.from_user.id in l:
        await message.answer("Доступные команды:\n"
                             '"/open_shift" - открытие смены\n'
                             '"/close_shift" - закрытие смены\n'
                             '"/ready_for_buyer" - поиск ожидающих покупателей\n'
                             '"/dialog_stop" - закрыть диалог с покупателем и найти следующего ожидающего покупателя\n'
                             '"/queue" - просмотр количества ожидающих покупателей')
    else:
        await message.answer("Доступные команды:\n"
                             '"/manager" - поиск свободного менеджера')


@dp.message(Command(commands=pin))
async def process_register_command(message: Message):
    tg_id = message.chat.id
    flag = bool(message.from_user.username)
    if flag:
        name = message.from_user.username
    else:
        name = 'not username'
    t = await functional_man.registration(tg_id, name)
    await message.answer(text=t)


@dp.message(Command(commands="delete_me"))
async def process_delete_command(message: Message):
    t = await functional_man.delete_man(message.from_user.username)
    await message.answer(t)


@dp.message(Command(commands="open_shift"))
async def process_open_shift_command(message: Message):
    c = await functional_man.open_status(message.from_user.id)
    await message.answer(c)


@dp.message(Command(commands='close_shift'))
async def process_close_shift_command(message: Message):
    c = await functional_man.close_status(message.from_user.id)
    await message.answer(c)


@dp.message(Command(commands="ready_for_buyer"))
async def process_open_state_command(message: Message):
    c = await functional_man.open_state(message.from_user.id)
    await message.answer(c)


@dp.message(Command(commands="manager"))
async def process_search_manager_command(message: Message):
    l = await functional_man.check_man("tg_id")
    if message.from_user.id in l:
        await message.answer("Вы менеджер, задайте вопрос сами себе")
    else:
        text = await functional_buy.distribution(message.from_user.id)
        await message.answer(text)


@dp.message(Command(commands="dialog_stop"))
async def process_dialog_stop_command(message: Message):
    t = await functional_man.open_state(message.from_user.id)
    await message.answer(t)


@dp.message(Command(commands="queue"))
async def check_queue_command(message: Message):
    l = await functional_man.check_man("tg_id")
    if message.from_user.id in l:
        t = await functional_buy.queue_buyer()
        await message.answer(f"В очереди сейчас: {len(t)}")
    else:
        await message.answer("Вы не являетесь работником магазина")


# этот хэндлер срабатывает на остальные сообщения
@dp.message()
async def chat(message: Message):
    try:
        l = await functional_man.search_two_id_man(message.from_user.id)
        man_id = int(l[0])
        buy_id = int(l[1])
        if message.from_user.id == man_id:
            await message.send_copy(chat_id=buy_id)
        else:
            await message.send_copy(chat_id=man_id)
    except:
        await message.answer("У вас нет открытого диалога")


async def main():
    await functional_man.creat_table_managers()
    await functional_buy.creat_table_buyer()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
