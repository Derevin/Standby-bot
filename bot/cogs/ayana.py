from discord.ext import commands
import discord
from settings import *
from inspect import Parameter


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

    @commands.command()
    async def sayd(self, ctx, *args):
        if not args:
            raise commands.errors.MissingRequiredArgument(
                Parameter("args", Parameter.VAR_POSITIONAL)
            )
        str = " ".join(args)
        msg = await ctx.channel.send((str + " "))
        await ctx.message.delete()
        await msg.edit(content=str)


def setup(bot):
    bot.add_cog(Ayana(bot))
