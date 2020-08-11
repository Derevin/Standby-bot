import asyncpg


async def ensure_guild_existence(bot, gid):
    guild = await bot.pg_pool.fetch("SELECT * FROM guild WHERE guild_id = $1", gid)

    if not guild:
        print("guild not in db yet")
        await bot.pg_pool.execute("INSERT INTO guild (guild_id) VALUES ($1)", gid)
