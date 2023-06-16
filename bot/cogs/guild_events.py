from nextcord.ext.commands import Cog

from db_integration import db_functions as db


class GuildEvents(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_guild_join(self, guild):
        await db.ensure_guild_existence(self.bot, guild.id)


    @Cog.listener()
    async def on_guild_update(self, before, after):
        await db.ensure_guild_existence(self.bot, after.id)


def setup(bot):
    bot.add_cog(GuildEvents(bot))
