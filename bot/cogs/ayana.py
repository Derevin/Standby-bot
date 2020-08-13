from discord.ext import commands
import discord
from settings import *


class Ayana(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id == GUILD_ID:
            channel = discord.utils.get(
                ctx.guild.text_channels, name=ERROR_CHANNEL_NAME
            )
            if channel is not None:
                await channel.send(f"{member} has been noscoped succesfully.")


def setup(bot):
    bot.add_cog(Ayana(bot))
