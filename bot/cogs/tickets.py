from discord.ext import commands
import discord
from settings import *


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        pass

    @commands.command()
    async def open(self, ctx, *args):
        pass

    @commands.command()
    async def reopen(self, ctx, *args):
        pass

    @commands.command()
    async def resolve(self, ctx, *args):
        pass


def setup(bot):
    bot.add_cog(Tickets(bot))
