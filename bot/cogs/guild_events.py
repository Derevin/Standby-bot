import discord
from discord.ext import commands
from db.db_func import ensure_guild_existence


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await ensure_guild_existence(self.bot, guild.id)

    @commands.Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild):
        await ensure_guild_existence(self.bot, after.id)


def setup(bot):
    bot.add_cog(GuildEvents(bot))
