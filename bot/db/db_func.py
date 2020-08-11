import asyncpg


async def ensure_guild_existence(bot, gid):
    guild = await bot.pg_pool.fetch("SELECT * FROM guild WHERE guild_id = $1", gid)

    if not guild:
        print(f"Adding guild {gid} to db.")
        await bot.pg_pool.execute("INSERT INTO guild (guild_id) VALUES ($1)", gid)


async def ensure_user_existence(bot, uid, gid):
    usr = await bot.pg_pool.fetch(
        "SELECT * FROM user WHERE user_id = $1 AND guild_id = $2", uid, gid
    )

    if not usr:
        print(f"Adding user {uid} with guild {gid} to db.")
        await bot.pg_pool.execute(
            "INSERT INTO user (user_id, guild_id, stars, thanks) VALUES ($1, $2, 0, 0)",
            uid,
            gid,
        )

