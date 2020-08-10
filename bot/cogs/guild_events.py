import discord
from discord.ext import commands


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def ensure_guild_existence(bot, gid):
    #     guild = await bot.pg_pool.fetch("SELECT * FROM guild WHERE guild_id = $1", gid)

    #     if not guild:
    #         print("guild not in db yet")
    #         await bot.pg_pool.execute("INSERT INTO guild (guild_id) VALUES ($1)", gid)

    # @commands.Cog.listener()
    # async def on_guild_join(self, guild: discord.Guild):
    #     await GuildEvents.ensure_guild_existence(self.bot, guild.id)

    # @commands.Cog.listener()
    # async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
    #     await GuildEvents.ensure_guild_existence(self.bot, after.id)


def setup(bot):
    bot.add_cog(GuildEvents(bot))
