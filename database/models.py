import asyncpg
from decouple import config


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
                trial_used bool,
                send_ref bool)
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
            id SERIAL PRIMARY KEY,
            code VARCHAR(3),
            name VARCHAR(255)
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
