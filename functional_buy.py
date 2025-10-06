import aiomysql
import random
from config import user, host, password, db_name
import functional_man

pool = None


async def init_pool():
    global pool
    pool = await aiomysql.create_pool(
        host=host,
        user=user,
        port=3306,
        password=password,
        db=db_name,
    )


async def close_pool():
    pool.close()
    await pool.wait_closed()


async def creat_table_buyer():
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                creat = "CREATE TABLE IF NOT EXISTS `buyer`(buy_id INT);"
                await cursor.execute(creat)
        await close_pool()
    except Exception as ex:
        await close_pool()
        print(ex)


async def derivation_buyer():  #выводим всех ожидающих покупателей
    c = []
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                select = "SELECT * FROM `buyer`;"
                await cursor.execute(select)
                cur = await cursor.fetchall()
                for k in cur:
                    for z in k:
                        c.append(z)
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()
        print(ex)


async def distribution(buy_id: int):
    l = await functional_man.cheek_free_managers()
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                if len(l) == 0:
                    add_buyer = "INSERT INTO `buyer`(buy_id)" \
                                "VALUES (%s);"
                    await cursor.execute(add_buyer, buy_id)
                    await conn.commit()
                    c = await queue()
                    return ("Сейчас все менеджеры заняты, вас обслужат как только менеджеры освободятся\n"
                            f"В очереди сейчас{len(c)}")
                else:
                    man = random.choice(l)
                    await functional_man.close_state(int(man), buy_id)
                    return "Сейчас подключится менеджер"
        await close_pool()
    except Exception as ex:
        return str(ex)
    finally:
        await close_pool()


async def delete_buy(buy_id: int):
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
        print(ex)


async def queue():
    l = []
    try:
        await init_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                select = "SELECT * FROM `buyer`"
                await cursor.execute(select)
                cur = await cursor.fetchall()
                for k in cur:
                    for z in k:
                        l.append(z)
        await close_pool()
        return l
    except Exception as ex:
        await close_pool()
        return ex
