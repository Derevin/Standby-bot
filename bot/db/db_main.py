import asyncpg
from db.create_scripts import create_tables
from settings import *


async def init_db_connection(bot):
    bot.pg_pool = await asyncpg.create_pool(DATABASE_URL)
    await create_tables(bot.pg_pool)
