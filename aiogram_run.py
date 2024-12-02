import asyncio

from create_bot import bot, dp
from handlers.admin_handlers import admin_router
from handlers.start import start_router, set_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db_users import check_end_subscribe
from database.models import create_table_if_not_exist


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_end_subscribe, 'interval', hours=24)
    scheduler.start()


async def main():
    await create_table_if_not_exist()
    start_scheduler()
    dp.include_router(admin_router)
    dp.include_router(start_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands()
    await dp.start_polling(bot)

try:
    if __name__ == '__main__':
        asyncio.run(main())
except KeyboardInterrupt as e:
    print(str(e))
