from discord.ext import commands
import discord
from settings import *
from inspect import Parameter
import re
import aiohttp
import random
import datetime


class Ayana(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Has the bot repeat a message")
    async def sayd(self, ctx, *args):
        if not args:
            raise commands.errors.MissingRequiredArgument(
                Parameter("args", Parameter.VAR_POSITIONAL)
            )
        str = " ".join(args)
        msg = await ctx.channel.send((str + " "))
        await ctx.message.delete()
        await msg.edit(content=str)

    @commands.command(
        aliases=["pfp"],
        brief="Displays the profile picture of a user. Also works as +pfp",
    )
    async def avatar(self, ctx, *args):

        args_joined = " ".join(args)

        if not args:
            user = ctx.author

        elif re.search(r"<@!?\d+>", args[0]):
            id = int(re.search(r"\d+", args[0]).group())
            user = discord.utils.get(ctx.guild.members, id=id)

        elif re.search(r".*#\d{4}$", args_joined):
            name, tag = re.split(" ?#", args_joined)
            user = discord.utils.get(ctx.guild.members, name=name, discriminator=tag)

        else:
            name = args_joined
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

    @commands.command(brief="Returns the Urban Dictionary definition of a word")
    async def urban(self, ctx, *query):
        if not query:
            raise commands.errors.MissingRequiredArgument("Please enter a valid query.")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "http://api.urbandictionary.com/v0/define?term=" + " ".join(query)
            ) as r:
                data = await r.json()
                if "error" in data:
                    await ctx.send("Server is not responding, please try again later.")
                    return
                if len(data["list"]) > 0:
                    entry = data["list"][0]
                    embed = discord.Embed(color=DARK_ORANGE)
                    embed.add_field(name="Word", value=entry["word"], inline=False)
                    embed.add_field(
                        name="Definition", value=entry["definition"], inline=False,
                    )
                    embed.add_field(
                        name="Example", value=entry["example"], inline=False
                    )
                    embed.add_field(name="Author", value=entry["author"], inline=False)
                    embed.add_field(
                        name="Rating",
                        value=(
                            str(entry["thumbs_up"])
                            + " :thumbsup: / "
                            + str(entry["thumbs_down"])
                            + " :thumbsdown:"
                        ),
                        inline=False,
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No definition found.")

    @commands.command(brief="Reposts the last 'user left' message to a channel")
    async def obit(self, ctx, channel_name):
        channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel:
            async for msg in ctx.channel.history(limit=5):
                if (
                    msg.author.id == BOT_ID
                    and msg.embeds
                    and msg.embeds[0].title == "The void grows smaller..."
                ):
                    await channel.send(embed=msg.embeds[0])
                    return
        await ctx.message.delete()


async def welcome_message(bot, payload):
    if payload.guild.id == GUILD_ID:
        general = discord.utils.get(payload.guild.text_channels, name="general")
        rules_ch = discord.utils.get(payload.guild.text_channels, name="rules")
        rules_text = rules_ch.mention if rules_ch else "rules"
        if general:
            message = (
                f"Welcome {payload.mention}!\n"
                "Wondering why the server seems so void of channels?\n"
                f"Please read the {rules_text} to unlock the full server!\n"
                "https://www.youtube.com/watch?v=67h8GyNgEmA"
            )
            await general.send(message)


async def kia_message(bot, payload):
    if payload.guild.id == GUILD_ID:
        channel = discord.utils.get(
            payload.guild.text_channels, name=ERROR_CHANNEL_NAME
        )
        if channel:
            name = payload.name
            time = datetime.datetime.now()
            time = time.strftime("%b %d, %H:%M")
            embed = discord.Embed(color=GREY)
            embed.title = "The void grows smaller..."
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/744224801429782679/747945281248559184/grave.png"
            )
            embed.description = f":rocket: {name} has left the void :rocket:"
            causes = [
                "ded",
                "Couldn't find their socks fast enough",
                "Yeeted themselves off a very high chair",
                "Forgot how to breathe",
                "Stickbugged one time too many",
                "Disrespected the pedestal",
                "Terminal case of being horny",
                "Sacrificed at the altar of Tzeentch",
                "Critical paper cut",
                "Executed by the ICC for their numerous war crimes in Albania",
            ]
            animu = discord.utils.get(payload.guild.text_channels, name="animu")
            if animu:
                causes.append(f"Too much time spent in {animu.mention}")
            embed.add_field(name="Time of death", value=time)
            embed.add_field(
                name="Cause of death", value=causes[random.randint(1, len(causes)) - 1]
            )
            await channel.send(embed=embed)


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
