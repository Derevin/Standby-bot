from discord.ext import commands
import discord
from settings import *
from utils.util_functions import *
from inspect import Parameter
import re
import aiohttp
import random
import datetime


class Services(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Makes the bot repeat a message")
    async def sayd(self, ctx, *, message):

        msg = await ctx.channel.send((message + " "))
        await ctx.message.delete()
        await msg.edit(content=message)

    @commands.command(
        aliases=["pfp"],
        brief="Displays the profile picture of a user. Also works as +pfp",
    )
    async def avatar(self, ctx, *user):

        query = " ".join(user)

        if not user:
            user = ctx.author

        elif ctx.message.mentions:
            user = ctx.message.mentions[0]

        else:
            user = get_user(ctx.guild, query)

        if user:
            embed = avatar_embed(user)
            await ctx.send(embed=embed)

        else:
            raise commands.errors.BadArgument(
                message="Enter a unique identifier - mention, nickname or username (tag optional) - or leave empty"
            )

    @commands.command(brief="Returns the Urban Dictionary definition of a word")
    async def urban(self, ctx, *, query):
        response = await urban_embed(query, 1)
        if isinstance(response, discord.Embed):
            message = await ctx.send(embed=response)
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("🇽")
        elif isinstance(response, str):
            await ctx.send(response)

    @commands.command(
        aliases=["sleaderboard", "starboard"],
        brief="Displays the starboard leaderboards. Also works as +sleaderboard, +starboard",
    )
    async def sbldr(self, ctx):
        starboard_ldr = await self.bot.pg_pool.fetch(
            f"SELECT usr_id, SUM(stars) as sum_stars "
            f"FROM starboard "
            f"WHERE usr_id IN "
            f"(SELECT usr_id FROM usr WHERE guild_id = {ctx.guild.id}) "
            f"GROUP BY usr_id "
            f"ORDER BY sum_stars DESC ;"
        )
        await ctx.channel.send(starboard_ldr)

    @commands.command(brief="Displays thanks leaderboard",)
    async def thnksldr(self, ctx):
        thanks_ldr = await self.bot.pg_pool.fetch(
            f"SELECT usr_id, SUM(thanks) as sum_thanks "
            f"FROM usr "
            f"WHERE guild_id = {ctx.guild.id} "
            f"GROUP BY usr_id "
            f"ORDER BY sum_thanks DESC ;"
        )
        await ctx.channel.send(thanks_ldr)


async def urban_handler(bot, payload):
    if isinstance(payload, discord.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if (
            payload.user_id != BOT_ID
            and not payload.member.bot
            and message.embeds
            and message.embeds[0]
            and message.embeds[0].title.startswith("Page")
            and payload.emoji.name in ["⬅️", "➡️", "🇽"]
        ):
            if payload.emoji.name == "🇽":
                await message.clear_reaction("⬅️")
                await message.clear_reaction("➡️")
                await message.clear_reaction("🇽")
            else:
                embed = message.embeds[0]
                print(embed)
                title = embed.title
                match = re.search(r"Page (\d+)\/(\d+)", title)
                page, pages = int(match.group(1)), int(match.group(2))
                query = re.search(r"\[(.*)\]", embed.fields[0].value).group(1)
                user = message.guild.get_member(payload.user_id)
                if payload.emoji.name == "⬅️" and page > 1:
                    embed = await urban_embed(query, page - 1)
                elif payload.emoji.name == "➡️" and page < pages:
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
    bot.add_cog(Services(bot))
