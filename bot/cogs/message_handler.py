import discord
from discord.ext import commands
from cogs.error_handler import unhandled_error_embed
from settings import *

from utils.regex import regex_handler


class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if str(message.channel.type) == "text":
            try:
                await regex_handler(self.bot, message)
            except Exception as e:
                if message.guild.id == GUILD_ID:
                    channel = discord.utils.get(
                        message.guild.text_channels, name=ERROR_CHANNEL_NAME
                    )
                    if channel is not None:
                        await channel.send(
                            embed=unhandled_error_embed(
                                message.content, message.channel, e
                            )
                        )


def setup(bot):
    bot.add_cog(MessageHandler(bot))
