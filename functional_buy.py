import aiomysql
import random
from config import user, host, password, db_name
import functional_man

pool = None


async def init_pool():  #инициализирует соединение с базой mysql
    global pool
    pool = await aiomysql.create_pool(
        host=host,
        user=user,
        port=3306,
        password=password,
        db=db_name,
    )


async def close_pool():  #закрывает соединение с базой mysql
    pool.close()
    await pool.wait_closed()


async def creat_table_buyer():  #создает таблицу ожидающих покупателей
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                creat = ("CREATE TABLE IF NOT EXISTS `buyer`(buy_id BIGINT,"
                         "buy_name VARCHAR(32),"
                         "search_managers CHAR(5) DEFAULT ('close'),"
                         "last_update DATE DEFAULT (CURRENT_DATE()),"
                         "command VARCHAR(500) DEFAULT (''));")
                await cursor.execute(creat)
        await close_pool()
    except Exception as ex:
        print(str(ex))
        await close_pool()


async def registration_buyer(buy_id: int, buy_tag: str):  #регистрирует менеджера в таблицу
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                add_manager = "INSERT INTO `buyer`(buy_id,buy_name,last_update)" \
                                f"VALUES ({buy_id}, '{buy_tag}',CURRENT_DATE());"
                await cursor.execute(add_manager)
                await conn.commit()
        await close_pool()
    except Exception as ex:
        await close_pool()
        print(str(ex))


async def queue_buyer():  #выводим всех ожидающих покупателей/очередь
    c = []
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                select = "SELECT buy_id FROM `buyer`;"
                await cursor.execute(select)
                cur = await cursor.fetchall()
                for k in cur:
                    for z in k:
                        c.append(z)
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()


async def distribution(buy_id: int):  #перенаправляет покупателей на менеджеров
    l = await functional_man.check_free_managers()
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                if len(l) == 0:
                    add_buyer = "INSERT INTO `buyer`(buy_id)" \
                                f"VALUES ({buy_id});"
                    await cursor.execute(add_buyer)
                    await conn.commit()
                    c = await queue_buyer()
                    if len(c) == 0:
                        return ("Сейчас все менеджеры заняты, вас обслужат как только менеджеры освободятся\n"
                                f"Ваш номер 1")
                    else:
                        return ("Сейчас все менеджеры заняты, вас обслужат как только менеджеры освободятся\n"
                                f"Ваш номер {len(c)}")
                else:
                    man = random.choice(l)
                    await functional_man.close_state(int(man), buy_id)
                    return ("Сейчас подключится менеджер\n"
                            "Можете задать свой вопрос")
    except Exception as ex:
        return str(ex)
    finally:
        await close_pool()


async def delete_buy(buy_id: int):  #удаляем покупателя из субд
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                delete = f"DELETE FROM `buyer` WHERE buy_id={buy_id};"
                await cursor.execute(delete)
                await conn.commit()
        await close_pool()
    except Exception as ex:
        await close_pool()
