from nextcord.ext import commands
import nextcord
from nextcord import Interaction, SlashOption
from settings import *
from utils.util_functions import *
from inspect import Parameter
import re
import aiohttp
import random
import datetime
from db.db_func import get_or_insert_usr
from dataclasses import dataclass


@dataclass
class LeaderboardSettings:
    title: str
    stat_name: str
    stat_col_name: str
    user_name: str = "User"
    color: str = VIE_PURPLE
    table: str = "usr"
    stat_embed_header: str = None


all_settings = {
    "Stars": LeaderboardSettings(
        title="Stars leaderboard",
        stat_name="Stars",
        stat_col_name="stars",
        color=STARBOARD_COLOUR,
        table="starboard",
    ),
    "Voids": LeaderboardSettings(
        title="Voids leaderboard",
        stat_name="Voids",
        stat_col_name="thanks",
    ),
    "Skulls": LeaderboardSettings(
        title="Skulls leaderboard",
        stat_name="Skulls",
        stat_col_name="skulls",
        stat_embed_header="💀",
        user_name="Metalhead",
    ),
    "Roulette (current)": LeaderboardSettings(
        title="Stars leaderboard",
        stat_name="Current roulette streak",
        stat_col_name="current_roulette_streak",
        stat_embed_header="Rounds",
    ),
    "Roulette (all-time)": LeaderboardSettings(
        title="Stars leaderboard",
        stat_name="All-time best roulette streak",
        stat_col_name="max_roulette_streak",
        stat_embed_header="Rounds",
    ),
}


class Services(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Makes the bot repeat a message", hidden=True)
    async def sayd(self, ctx, *, message):

        msg = await ctx.channel.send((message + " "))
        await ctx.message.delete()
        await msg.edit(content=message)

    @nextcord.slash_command(
        guild_ids=[GUILD_ID],
        description="Displays a user's profile picture.",
    )
    async def avatar(
        self,
        interaction: Interaction,
        user: nextcord.User = SlashOption(
            description="The target user",
        ),
    ):
        await interaction.send(embed=avatar_embed(user))

    @nextcord.slash_command(
        guild_ids=[GUILD_ID],
        description="Returns the Urban Dictionary definition of a word or phrase",
    )
    async def urban(
        self,
        interaction: Interaction,
        query=SlashOption(description="The word or phase to look up"),
    ):
        response = await urban_embed(query, 1)
        if isinstance(response, nextcord.Embed):
            await interaction.send(embed=response)
            message = await interaction.original_message()
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("🇽")
        elif isinstance(response, str):
            await interaction.send(response)

    @nextcord.slash_command(
        guild_ids=[GUILD_ID], description="Displays the leaderboards"
    )
    async def leaderboard(
        self,
        interaction: Interaction,
        stat=SlashOption(
            name="leaderboard",
            description="The leaderboard to display",
            choices=all_settings.keys(),
        ),
    ):

        settings = all_settings[stat]

        leaderboard = await create_leaderboard(self.bot, settings, interaction.guild.id)

        embed = build_leaderboard_embed(interaction, leaderboard, settings)

        await interaction.send(embed=embed)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Award a skull.")
    async def skull(
        self,
        interaction: Interaction,
        recipient: nextcord.User = SlashOption(
            description="The user to award a skull to"
        ),
    ):

        if not interaction.user.id == JORM_ID:
            await interaction.send(
                GIT_STATIC_URL + "/images/memes/You%20have%20no%20power%20here.png"
            )
            return

        await get_or_insert_usr(self.bot, recipient.id, recipient.guild.id)

        await self.bot.pg_pool.execute(
            f"UPDATE usr SET skulls = skulls + 1 WHERE usr_id = {recipient.id}"
        )
        await interaction.send(f"Gave a 💀 to {recipient.mention}")

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Look up a user's stats")
    async def stats(
        self,
        interaction,
        user: nextcord.User = SlashOption(description="User to look up"),
        stat=SlashOption(
            description="Stat to look up", choices=["Everything", *all_settings.keys()]
        ),
    ):

        if stat != "Everything":
            settings = all_settings[stat]
            stats = await create_leaderboard(self.bot, settings, filter_by_user=user)
            if not stats:
                await interaction.send(
                    f"{user.mention} currently has no {settings.stat_name.lower()}."
                )
            elif "Roulette" in stat:
                await interaction.send(
                    f"""{user.mention}'s {settings.stat_name.lower()} is {stats[0]['total']} rounds."""
                )
            else:
                await interaction.send(
                    f"{user.mention} currently has {stats[0]['total']} {settings.stat_name.lower()}."
                )
        else:
            message = f"{user.mention}'s current stats are:\n"
            for settings in all_settings.values():
                stats = await create_leaderboard(
                    self.bot, settings, filter_by_user=user
                )
                message += (
                    f"{settings.stat_name}: {stats[0]['total'] if stats else 0}\n"
                )
            await interaction.send(message)


async def create_leaderboard(bot, settings, guild_id=GUILD_ID, filter_by_user=None):

    filter_condition = (
        "AND usr_id = " + str(filter_by_user.id) if filter_by_user else ""
    )

    leaderboard = await bot.pg_pool.fetch(
        f"SELECT usr_id, SUM({settings.stat_col_name}) as total "
        f"FROM {settings.table} "
        f"WHERE usr_id IN "
        f"(SELECT usr_id FROM usr WHERE guild_id = {guild_id}{filter_condition}) "
        f"GROUP BY usr_id "
        f"HAVING SUM({settings.stat_col_name}) > 0"
        f"ORDER BY total DESC ;"
    )
    return leaderboard


def build_leaderboard_embed(
    interaction,
    leaderboard,
    settings,
    count_col_name="total",
    usr_col_name="usr_id",
    max_print=12,
):

    if not leaderboard:
        return nextcord.Embed(
            color=settings.color,
            description=f"The {settings.title} is currently empty.",
        )
    ljust_num = len(str(settings.stat_name)) if str(settings.stat_name).isalnum() else 3
    ldr = []
    cnt = 0

    prev_count = -1
    keep_printing = True
    for rec in leaderboard:
        cnt += 1
        if cnt > max_print:
            keep_printing = False

        if (
            keep_printing
            or prev_count == rec[count_col_name]
            or interaction.user.id == rec[usr_col_name]
        ):
            usr = interaction.guild.get_member(rec[usr_col_name])
            if usr:
                num_spaces = ljust_num - len(str(rec[count_col_name])) + 1
                spaces = EMPTY2 * num_spaces
                ldr.append(
                    f"{rec[count_col_name]}{spaces} {usr.name}#{usr.discriminator}"
                )
            if keep_printing:
                prev_count = rec[count_col_name]

    header_merged = f"{settings.stat_name}\t{settings.user_name}"

    merged_str = ""
    for line in ldr:
        merged_str += f"{line}\n"

    embed = nextcord.Embed(color=settings.color)
    embed.add_field(name=header_merged, value=merged_str)
    embed.title = settings.title
    return embed


async def urban_handler(bot, payload):
    if isinstance(payload, nextcord.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
            if (
                payload.user_id != BOT_ID
                and not payload.member.bot
                and message.embeds
                and message.embeds[0]
                and str(message.embeds[0].title).startswith("Page")
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
                    if payload.emoji.name == "⬅️" and page > 1:
                        embed = await urban_embed(query, page - 1)
                    elif payload.emoji.name == "➡️" and page < pages:
                        embed = await urban_embed(query, page + 1)

                    await message.remove_reaction(payload.emoji, user)
                    await message.edit(embed=embed)
        except Exception:
            pass


def avatar_embed(user: nextcord.User) -> nextcord.Embed:
    embed = nextcord.Embed(color=PALE_GREEN)
    link = user.display_avatar.url if user.display_avatar else ""
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
                embed = nextcord.Embed(color=DARK_ORANGE)
                embed.title = f"Page {page}/{pages}"
                word = entry["word"]
                web_link = f"https://www.urbandictionary.com/define.php?term={word}"
                web_link = re.sub(" ", "%20", web_link)
                embed.add_field(
                    name="Word",
                    value=f"[{word}]({web_link})",
                    inline=False,
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
