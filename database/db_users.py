import asyncpg
from decouple import config

from datetime import datetime, timedelta


from work_time.time_func import *
from create_bot import bot
from outline.main import get_key_id_from_url, delete_key


async def create_table_if_not_exist():
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        tables = {
            'users': '''
            CREATE TABLE users(
                user_id INT8 PRIMARY KEY,
                name TEXT,
                is_admin bool,
                is_subscriber bool,
                vpn_key TEXT,
                payment_label TEXT,
                start_subscribe date,
                end_subscribe date,
                balance INT4,
                invited_by_id INT8,
                trial_used bool)
            ''',

            'promocodes': '''
            CREATE TABLE promocodes(
                promo TEXT,
                time INT4)
            ''',

            'servers': '''
            CREATE TABLE servers(
                server_id INT4,
                country_id INT2,
                server_ip VARCHAR,
                server_password VARCHAR,
                outline_url VARCHAR,
                outline_cert VARCHAR,
                is_active bool,
                max_users INT4,
                vless_port INT4,
                manager_port INT4
                )
                
            ''',
            'countries': '''
            CREATE TABLE countries(
            )
            '''
        }

        for table_name, create_sql in tables.items():
            table_exists = await con.fetchval(f"""
            SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = $1
                )
            """, table_name)
            if not table_exists:
                await con.execute(create_sql)
                print(f'Table {table_name} successfully created!')
            else:
                print(f'Table {table_name} already exists')
    finally:
        if con:
            await con.close()


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


async def new_user(user_id,
                   username: str = 'None',
                   is_admin=False,
                   is_subscriber: bool = False,
                   balance: int = 0,
                   invited_by_id: int = None,
                   trial_used: bool = False,
                   send_ref: bool = False):
    con = None

    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
            INSERT INTO users(user_id, name, is_admin, is_subscriber, 
            balance, invited_by_id, trial_used, send_ref) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            '''

        await con.execute(query, user_id, username, is_admin, is_subscriber,
                          balance, invited_by_id, trial_used, send_ref)

    finally:
        if con:
            await con.close()


async def get_user_info(user_id, param: int = None):
    """
        1 - name str,
        2 - is_admin bool,
        3 - is_subscriber bool,
        4 - vpn_key str,
        5 - payment_label TEXT,
        6 - start_subscribe date,
        7 - end_subscribe date
        8 - balance INT4
        9 - invited_by_id INT8
        10 - trial_used bool
        11 - send_ref
    """
    con = None

    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
            SELECT * 
            FROM users 
            WHERE user_id = $1
                    '''

        result = await con.fetchrow(query, user_id)

        if result:
            if param is not None:
                return result[param]
            return (
                result['user_id'], result['name'], result['is_admin'], result['is_subscriber'],
                result['vpn_key'], result['payment_label'], result['start_subscribe'],
                result['end_subscribe'], result['balance'], result['invited_by_id'],
                result['trial_used'], result['send_ref']
            )
        return False

    finally:
        if con:
            await con.close()


async def pop_promo(code: str):

    con = None

    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        SELECT promo, time 
        FROM promocodes 
        WHERE promo = $1
                    '''

        result = await con.fetchrow(query, code)

        if result:
            query = '''
            DELETE FROM promocodes 
            WHERE promo = $1       
                        '''

            await con.execute(query, code)

            return result
        return False

    finally:
        if con:
            await con.close()


async def add_label(user_id, label: str):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users 
        SET payment_label = $1
        WHERE user_id = $2
                    '''

        await con.execute(query, label, user_id)

    finally:
        if con:
            await con.close()


async def del_label(user_id):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users 
        SET payment_label = null 
        WHERE user_id = $1
            '''

        await con.execute(query, user_id)

    finally:
        if con:
            await con.close()


async def set_for_subscribe(user_id, buy_on):
    """
    buy_on - кол-во дней подписки
    """

    start_time, end_time = get_time_for_subscribe(buy_on)
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users SET is_subscriber = True,
        start_subscribe = $1,
        end_subscribe = $2, 
        payment_label = null ,
        trial_used = TRUE
        WHERE user_id = $3
               '''

        await con.execute(query, start_time, end_time, user_id)

    finally:
        if con:
            await con.close()

async def set_for_trial_subscribe(user_id):

    start_time, end_time = get_time_for_test_subscribe()
    con = None

    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users 
        SET is_subscriber = True,
        start_subscribe = $1,
        end_subscribe = $2,
        trial_used = TRUE
        WHERE user_id = $3
               '''
        await con.execute(query, start_time, end_time, user_id)

    finally:
        if con:
            await con.close()


async def set_for_unsubscribe(user_id):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users 
        SET is_subscriber = False,
        vpn_key = null, 
        start_subscribe = null,
        end_subscribe = null
        WHERE user_id = $1
            '''
        await con.execute(query, user_id)

    finally:
        if con:
            await con.close()


async def set_user_vpn_key(user_id, key: str):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users 
        SET vpn_key = $1 
        WHERE user_id = $2
        '''

        await con.execute(query, key, user_id)

    except Exception as e:
        print(str(e))

    finally:
        if con:
            await con.close()


async def update_username(user_id, username: str):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = '''
        UPDATE users 
        SET name = $1 
        WHERE user_id = $2
        '''

        await con.execute(query, username, user_id)
    except Exception as e:
        print(str(e))
    finally:
        if con:
            await con.close()


async def check_end_subscribe():
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))

        query_ended = """
        SELECT user_id, vpn_key
        FROM users
        WHERE end_subscribe <= $1
        """
        query_end_soon = """
        SELECT user_id, end_subscribe
        FROM users
        WHERE end_subscribe < $1 AND end_subscribe >= $2
        """
        now = datetime.now()  # Сегодняшняя дата
        later3days = now + timedelta(days=3)
        later2days = now + timedelta(days=2)
        end_soon_users = await con.fetch(query_end_soon, later3days, later2days)

        for user in end_soon_users:
            user_id = user['user_id']
            end_subscribe = user['end_subscribe']
            await bot.send_message(user_id, f'‼️Уважаемый пользователь‼️\nВаша подписка закончится {end_subscribe}\n'
                                            'VPN ключ будет деактивирован.\n'
                                            'Для продления подписки введите команду /buy')

        ended_sub_users = await con.fetch(query_ended, now)  # Нахождение пользователей с закончившейся подпиской

        for user in ended_sub_users:
            user_id = user['user_id']
            key = user['vpn_key']
            await bot.send_message(user_id, '‼️Уважаемый пользователь‼️\nВаша подписка закончилась.\n'
                                            'VPN ключ деактивирован.\n'
                                            'Для покупки продления подписки введите команду /buy')
            key_id = await get_key_id_from_url(key)
            await delete_key(key_id)
            await set_for_unsubscribe(user_id)

    except Exception as e:
        print(str(e))

    finally:
        await con.close()

async def get_sub_ids():
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = """
         SELECT user_id
         FROM users
         WHERE is_subscriber = True
         """
        ids = await con.fetch(query)
        return [record['user_id'] for record in ids]
    except Exception as e:
        print(e)
    finally:
        if con:
            await con.close()

async def get_all_ids():
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query = """
         SELECT user_id
         FROM users
         """
        ids = await con.fetch(query)
        return [record['user_id'] for record in ids]
    except Exception as e:
        print(e)
    finally:
        if con:
            await con.close()

# async def check_referer(user_id):
#     con = None
#     try:
#         con = await asyncpg.connect(dsn=config('DATABASE_URL'))
#         query = """
#         SELECT invited_by_id
#         FROM users
#         WHERE user_id = $1
#         """, user_id
#
#         referer = await con.fetch(query)
#         return referer
#
#     except Exception as e:
#         print(e)
#
#     finally:
#         if con:
#             await con.close()

async def add_balance_for_refer(to_user_id, by_user_id):
    con = None
    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        query_pay = """
        UPDATE users
        SET balance = balance + $1
        WHERE user_id = $2
        """

        await con.execute(query_pay, 25, to_user_id)

        query_set = """
        UPDATE users
        SET send_ref = TRUE
        WHERE user_id = $1
        """

        await con.execute(query_set, by_user_id)
        return True

    except Exception as e:
        print(e)

    finally:
        if con:
            await con.close()

async def extension_subscribe(user_id, amount_days: int):
    con = None

    try:
        con = await asyncpg.connect(dsn=config('DATABASE_URL'))
        get_query = """
        SELECT end_subscribe
        FROM users
        WHERE user_id = $1
        """
        end_sub_at_this_moment = await con.fetchval(get_query, user_id)

        new_end_subscribe = (end_sub_at_this_moment + timedelta(days=amount_days))

        set_query = """
        UPDATE users
        SET end_subscribe = $1
        WHERE user_id = $2
        """
        await con.execute(set_query, new_end_subscribe, user_id)

    except Exception as e:
        print(e)

    finally:
        if con:
            await con.close()