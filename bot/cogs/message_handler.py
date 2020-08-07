import discord
from discord.ext import commands

from utils.regex import regex_handler


class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if str(message.channel.type) == "text":
            await regex_handler(message)


def setup(bot):
    bot.add_cog(MessageHandler(bot))
