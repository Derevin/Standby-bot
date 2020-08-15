from discord.ext import commands
import discord
from settings import *
from inspect import Parameter
import re


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

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx, *args):

        args_joined = " ".join(args)

        if not args:
            user = ctx.author

        elif re.search(r"<@!?\d+>", args[0]):
            id = int(re.search(r"\d+", args[0]).group())
            user = discord.utils.get(ctx.guild.members, id=id)

        elif re.search(r".*#\d{4}$", args_joined):
            name, tag = re.split("#", args_joined)
            user = discord.utils.get(ctx.guild.members, name=name, discriminator=tag)

        else:
            name = " ".join(args)
            users = [
                user
                for user in ctx.guild.members
                if re.search(name, user.display_name, re.I)
            ]
            user = users[0] if len(users) == 1 else None

        if user:
            embed = avatar_embed(user)
            await ctx.send(embed=embed)

        else:
            raise commands.errors.BadArgument(
                message="Enter a unique identifier - mention, nickname or username with tag - or leave empty"
            )


def avatar_embed(user: discord.User) -> discord.Embed:
    embed = discord.Embed(color=PALE_GREEN)
    link = user.avatar_url
    embed.set_image(url=link)
    embed.title = user.display_name + " (" + str(user) + ")"
    text = "Direct Link"
    embed.description = f"[{text}]({link})"
    return embed


def setup(bot):
    bot.add_cog(Ayana(bot))
