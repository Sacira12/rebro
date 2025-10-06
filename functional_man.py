import aiomysql
import random
from config import user, host, password, db_name

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


async def creat_table_managers():
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


async def registration(tg_id: int, manager_tag: str):
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


async def open_status(tg_id: int):
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


async def close_status(tg_id: int):
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


async def open_state(tg_id: int):
    try:
        await init_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                l = await cheek_man('tg_id')
                if tg_id in l:
                    select = f"SELECT work_status FROM `managers` WHERE tg_id={tg_id};"
                    await cursor.execute(select, tg_id)
                    cur = await cursor.fetchall()
                    cur = cur[0]
                    if 'open' in cur:
                        insert = "UPDATE `managers`" \
                                 "SET state='free'," \
                                 "buyer_id= 0 " \
                                 "WHERE tg_id=%s;"
                        await cursor.execute(insert, tg_id)
                        await conn.commit()
                        c = "скоро соединим с покупателем"
                    else:
                        c = 'смена не открыта'
                else:
                    c = "Вы не являетесь работником магазина"
        await close_pool()
        return c
    except Exception as ex:
        await close_pool()
        return str(ex)


async def close_state(tg_id: int, buy_id: int):
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


async def cheek_free_managers():
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
        print(ex)


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


async def delete_man(manager_tag: str):
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


async def cheek_man(s: str):
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
