import aiomysql
import random
from config import user, host, password, db_name
import functional_buy

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


async def creat_table_managers():  #создает таблицу мэнэджеров
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                creat = "CREATE TABLE IF NOT EXISTS `managers`(manager_tag VARCHAR(32)," \
                        "tg_id BIGINT," \
                        "work_status CHAR(5) DEFAULT ('close')," \
                        "state CHAR(5) DEFAULT ('busy')," \
                        "buyer_id INT DEFAULT 0, PRIMARY KEY (manager_tag));"
                await  cursor.execute(creat)
        await close_pool()
    except Exception as ex:
        await close_pool()
        return ex


async def registration(tg_id: int, manager_tag: str):  #регистрирует менеджера в таблицу
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                l = await cheek_man('tg_id')
                if tg_id in l:
                    return "Вы были раннее уже зарегестрированы."
                else:
                    add_manager = "INSERT INTO `managers`(manager_tag,tg_id)" \
                                  f"VALUES ('{manager_tag}', {tg_id});"
                    await cursor.execute(add_manager)
                    await conn.commit()
                    c = "Вы успешно были зарегестрированы."
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()
        return str(ex)


async def open_status(tg_id: int):  #открывает смену
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                l = await cheek_man('tg_id')
                if tg_id in l:
                    insert = "UPDATE `managers`" \
                             "SET work_status='open'" \
                             f"WHERE tg_id={tg_id};"
                    c = 'Cмена открыта'
                    await cursor.execute(insert)
                    await conn.commit()
                else:
                    c = "Вы не являетесь работником магазина"
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()
        return str(ex)


async def close_status(tg_id: int): #закрывает смену
    try:
        await init_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                l = await cheek_man('tg_id')
                if tg_id in l:
                    insert = "UPDATE `managers`" \
                             "SET work_status='close'," \
                             "state = 'busy'," \
                             "buyer_id = 0 " \
                             f"WHERE tg_id={tg_id};"
                    c = "смена закрыта"
                    await cursor.execute(insert)
                    await conn.commit()
                else:
                    c = "Вы не являетесь работником магазина"
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()
        return str(ex)


async def open_state(tg_id: int):  #открывает поиск покупателей
    try:
        await init_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                g = await functional_buy.derivation_buyer()
                l = await cheek_man('tg_id')
                if tg_id in l:
                    select = f"SELECT work_status FROM `managers` WHERE tg_id={tg_id};"
                    await cursor.execute(select)
                    cur = await cursor.fetchall()
                    cur = cur[0]
                    if 'open' in cur:
                        insert = "UPDATE `managers`" \
                                 "SET state='free'," \
                                 "buyer_id= 0 " \
                                 f"WHERE tg_id={tg_id};"
                        await cursor.execute(insert)
                        await conn.commit()
                        if len(g) != 0:
                            await close_state(tg_id, int(g[0]))
                            c = "Соединяем с покупателем"
                        else:
                            c = "скоро соединим с покупателем"
                    else:
                        c = 'смена не открыта'
                else:
                    c = "Вы не являетесь работником магазина"
        await close_pool()
        if c == "Соединяем с покупателем":
            await functional_buy.delete_buy(int(g[0]))
        return c
    except Exception as ex:
        await close_pool()
        return str(ex)


async def close_state(tg_id: int, buy_id: int):  # закрывает поиск покупателей
    try:
        await init_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                insert = "UPDATE `managers`" \
                         "SET state='busy'," \
                         f"buyer_id='{buy_id}'" \
                         f"WHERE tg_id={tg_id};"
                await cursor.execute(insert)
                await conn.commit()
        await close_pool()
    except Exception as ex:
        await close_pool()
        print(ex)


async def cheek_free_managers(): #возвращает список свободный для общения менеджеров
    l = []
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                select = "SELECT tg_id FROM `managers` WHERE work_status='open' and state='free';"
                await cursor.execute(select)
                cur = await cursor.fetchall()
                for k in cur:
                    for z in k:
                        l.append(z)
        await close_pool()
        return l
    except Exception as ex:
        await close_pool()
        return str(ex)


async def for_me():
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                select = "SELECT * FROM `managers`;"
                await cursor.execute(select)
                cur = await cursor.fetchall()
                for cu in cur:
                    print(cu)
        print(cur)
        await close_pool()
    except Exception as ex:
        await close_pool()
        print(ex)


async def delete_man(manager_tag: str):  #удаляет мэнэджера из субд
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                l = await cheek_man('manager_tag')
                if manager_tag not in l:
                    с = "Вас нет в базе данных"
                else:
                    delete = f"DELETE FROM `managers` WHERE manager_tag='{manager_tag}';"
                    await cursor.execute(delete)
                    await conn.commit()
                    с = "Вы были удалены из субд"
        await close_pool()
        return с
    except Exception as ex:
        await close_pool()
        return ex


async def cheek_man(s: str):  #проверяет наличие менеджера в таблице субд
    c = []
    try:
        await init_pool()
        async with pool.acquire() as conn:  # получаем соединение из пула
            async with conn.cursor() as cursor:
                select = f"SELECT {s} FROM `managers`;"
                await cursor.execute(select)
                cur = await cursor.fetchall()
                for k in cur:
                    for z in k:
                        c.append(z)
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()
        return ex


async def search_two_id_man(tg_id: int):
    l=[]
    try:
        await init_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                c = await cheek_man("tg_id")
                if tg_id in c:
                    man = f"SELECT tg_id FROM `managers` WHERE tg_id={tg_id};"
                    buy = f"SELECT buyer_id FROM `managers` WHERE tg_id={tg_id};"
                else:
                    man = f"SELECT tg_id FROM `managers` WHERE buyer_id={tg_id};"
                    buy = f"SELECT buyer_id FROM `managers` WHERE buyer_id={tg_id};"
                await cursor.execute(man)
                cur = await cursor.fetchone()
                l.append(cur[0])
                await cursor.execute(buy)
                cur = await cursor.fetchone()
                l.append(cur[0])
        await close_pool()
        return l
    except Exception as ex:
        await close_pool()
        return str(ex)


