import asyncpg

from decouple import config

async def add_promo(code: str, time: int):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = f'''
            INSERT INTO promocodes(promo, time) 
            VALUES ($1, $2)
            '''

        await con.execute(query, code, time)

    finally:
        if con:
            await con.close()


async def del_promo(code: str):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
            DELETE FROM promocodes 
            WHERE promo = $1
            '''

        await con.execute(query, code)

    finally:
        if con:
            await con.close()