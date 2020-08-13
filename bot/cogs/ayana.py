from discord.ext import commands
import discord


class Ayana(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Ayana(bot))
