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

    @commands.command(brief="Makes the bot repeat a message")
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
                if (
                    re.search(name, user.display_name, re.I)
                    or re.search(name, user.name, re.I)
                )
            ]
            user = users[0] if len(users) == 1 else None

        if user:
            embed = avatar_embed(user)
            await ctx.send(embed=embed)

        else:
            raise commands.errors.BadArgument(
                message="Enter a unique identifier - mention, nickname or username (tag optional) - or leave empty"
            )

    @commands.command(brief="Returns the Urban Dictionary definition of a word")
    async def urban(self, ctx, *query):
        if not query:
            raise commands.errors.MissingRequiredArgument("Please enter a valid query.")
        query = " ".join(query)
        response = await urban_embed(query, 1)
        if isinstance(response, discord.Embed):
            message = await ctx.send(embed=response)
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("🇽")
        elif isinstance(response, str):
            await ctx.send(response)

    @commands.command(brief="Posts a random 'horny' warning")
    async def horny(self, ctx):
        links = [
            "https://cdn.discordapp.com/attachments/267554564838785024/667115013412225054/image0.jpg",
            "https://i.kym-cdn.com/entries/icons/original/000/033/758/Screen_Shot_2020-04-28_at_12.21.48_PM.png",
            "https://cdn.discordapp.com/attachments/267554564838785024/701271178790305852/horny.jpg",
            "https://cdn.discordapp.com/attachments/267554564838785024/708425147064909944/x3x53kej4jr31.png",
            "https://cdn.discordapp.com/attachments/258941607238172673/717436181901475990/anti_horny.jpg",
            "https://cdn.discordapp.com/attachments/620408411393228809/724613520318267422/ubil7fxr99551.png",
        ]
        await ctx.message.delete()
        await ctx.channel.send(links[random.randint(0, len(links) - 1)])

    @commands.command(brief="Posts an 'anime' warning")
    async def anime(self, ctx):
        await ctx.message.delete()
        await ctx.channel.send(
            "https://cdn.discordapp.com/attachments/355732809224028161/709500701134422137/anime_violation.png"
        )

    @commands.command(brief="Posts a 'cringe' warning")
    async def cringe(self, ctx):
        await ctx.message.delete()
        await ctx.send(
            "https://cdn.discordapp.com/attachments/441286267548729345/709160523907989524/EVACI9dUcAQp2Mb.png"
        )


async def urban_handler(bot, payload):
    if isinstance(payload, discord.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if (
            payload.user_id != BOT_ID
            and message.embeds
            and message.embeds[0].title.startswith("Page")
            and payload.emoji.name in ["⬅️", "➡️", "🇽"]
        ):
            if payload.emoji.name == "🇽":
                await message.clear_reaction("⬅️")
                await message.clear_reaction("➡️")
                await message.clear_reaction("🇽")
            else:
                embed = message.embeds[0]
                title = embed.title
                match = re.search(r"Page (\d+)\/(\d+)", title)
                page, pages = int(match.group(1)), int(match.group(2))
                query = re.search(r"\[(.*)\]", embed.fields[0].value).group(1)
                user = message.guild.get_member(payload.user_id)
                if payload.emoji.name == "⬅️" and page != 1:
                    embed = await urban_embed(query, page - 1)
                elif payload.emoji.name == "➡️" and page != pages:
                    embed = await urban_embed(query, page + 1)

                await message.remove_reaction(payload.emoji, user)
                await message.edit(embed=embed)


def avatar_embed(user: discord.User) -> discord.Embed:
    embed = discord.Embed(color=PALE_GREEN)
    link = user.avatar_url
    embed.set_image(url=link)
    embed.title = user.display_name + " (" + str(user) + ")"
    text = "Direct Link"
    embed.description = f"[{text}]({link})"
    return embed


async def urban_embed(query, page):

    async with aiohttp.ClientSession() as cs:
        api_link = f"https://api.urbandictionary.com/v0/define?term={query}"
        async with cs.get(api_link) as r:
            data = await r.json()
            if "error" in data:
                return "Server is not responding, please try again later."
            if len(data["list"]) > 0:
                entries = data["list"]
                pages = len(entries)
                entry = entries[page - 1]
                embed = discord.Embed(color=DARK_ORANGE)
                embed.title = f"Page {page}/{pages}"
                word = entry["word"]
                web_link = f"https://www.urbandictionary.com/define.php?term={word}"
                web_link = re.sub(" ", "%20", web_link)
                embed.add_field(
                    name="Word", value=f"[{word}]({web_link})", inline=False,
                )
                embed.add_field(
                    name="Definition",
                    value=entry["definition"][:1018] + " [...]",
                    inline=False,
                )
                embed.add_field(name="Example", value=entry["example"], inline=False)
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
                return embed
            else:
                return "No definition found."


def setup(bot):
    bot.add_cog(Ayana(bot))
