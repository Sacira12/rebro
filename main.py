import asyncio

import functional_buy
import functional_man
import config
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
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


# этот хэндлер срабатывает на остальные сообщения
@dp.message()
async def managers(message: Message):
    if message.text == pin:
        tg_id = message.chat.id
        flag = bool(message.from_user.username)
        if flag:
            name = message.from_user.username
        else:
            name = 'not username'
        t = await functional_man.registration(tg_id, name)
        await message.answer(text=t)
        if message.text.lower() == "увольняюсь":
            t = await functional_man.delete_man(message.from_user.username)
            await message.answer(t)


@dp.message
async def status(message: Message):
    if message.text.lower() == "открыть смену":
        c = await functional_man.open_status(message.from_user.id)
        await message.answer(c)
    if message.text.lower() == "закрыть смену":
        c = await functional_man.close_status(message.from_user.id)
        await message.answer(c)


@dp.message
async def state(message: Message):
    if message.text.lower() == "готов к покупателям":
        c = await functional_man.open_state(message.from_user.id)
        await message.answer(c)


@dp.message
async def menn(message: Message):
    if message.text == '/manager':
        await bot.send_message(53487, 'dvreagv')
        #должны проверить свободных менеджеров и соединить их с покупателем


async def main():
    await functional_man.creat_table_managers()
    await functional_buy.creat_table_buyer()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
