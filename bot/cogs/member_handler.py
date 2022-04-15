import nextcord
from nextcord.ext import commands
from cogs.rules import leave_message, welcome_message, level3_handler


class MemberHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, payload):
        await leave_message(self.bot, payload)

    @commands.Cog.listener()
    async def on_member_join(self, payload):
        await welcome_message(self, payload)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await level3_handler(before, after)


def setup(bot):
    bot.add_cog(MemberHandler(bot))
