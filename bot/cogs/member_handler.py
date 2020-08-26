import discord
from discord.ext import commands
from cogs.ayana import kia_message, welcome_message


class MemberHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, payload):
        await kia_message(self.bot, payload)

    @commands.Cog.listener()
    async def on_member_join(self, payload):
        await welcome_message(self, payload)


def setup(bot):
    bot.add_cog(MemberHandler(bot))
