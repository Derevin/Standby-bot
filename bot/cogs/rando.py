import random

from discord.ext import commands


class Rando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Gives a random number between 1 and 100")
    async def roll(self, ctx):
        await ctx.send(random.randrange(1, 101))

    @commands.command(brief="Gives a random number between 1 and 6")
    async def dice(self, ctx):
        await ctx.send(random.randrange(1, 7))

    @commands.command(brief="Gives randomly heads or tails")
    async def coin(self, ctx):
        n = random.randint(0, 1)
        await ctx.send("Heads" if n == 1 else "Tails")


def setup(bot):
    bot.add_cog(Rando(bot))
