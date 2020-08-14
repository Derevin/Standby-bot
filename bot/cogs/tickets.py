from discord.ext import commands
import discord
from settings import *


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def tinit(self, ctx, *args):
        pass

    @commands.command()
    async def topen(self, ctx, *args):
        pass

    @commands.command()
    async def treopen(self, ctx, *args):
        pass

    @commands.command()
    async def tresolve(self, ctx, *args):
        pass


def setup(bot):
    bot.add_cog(Tickets(bot))
