# import asyncpg
# from db.create_scripts import create_tables
# from settings import *


# async def init_db_connection(bot):
#     bot.pg_pool = await asyncpg.create_pool(DATABASE_URL)
#     async with bot.pg_pool.acquire() as con:
#         await create_tables(con)
