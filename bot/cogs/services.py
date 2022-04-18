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
from db.db_func import ensure_usr_existence

THANKS_LDR_HEADER = "Voids leaderboard"
THANKS_LDR_THANKS_HEADER = "Voids"
THANKS_LDR_USER_HEADER = "User"
STARBOARD_LDR_HEADER = "Stars leaderboard"
STARBOARD_LDR_STARS_HEADER = "Stars"
STARBOARD_LDR_USER_HEADER = "User"
SKULLS_LDR_HEADER = "Skulls leaderboard"
SKULLS_LDR_SKULLS_HEADER = "💀"
SKULLS_LDR_USER_HEADER = "Metalhead"
MAX_LEADERBOARD_PRINT = 12


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
        leaderboard=SlashOption(
            description="The leaderboard to display",
            choices=["Stars", "Thanks", "Skulls"],
        ),
    ):

        args_dict = {
            "Stars": (
                "stars",
                "starboard",
                STARBOARD_COLOUR,
                STARBOARD_LDR_STARS_HEADER,
                STARBOARD_LDR_USER_HEADER,
                STARBOARD_LDR_HEADER,
            ),
            "Thanks": (
                "thanks",
                "usr",
                VIE_PURPLE,
                THANKS_LDR_THANKS_HEADER,
                THANKS_LDR_USER_HEADER,
                THANKS_LDR_HEADER,
            ),
            "Skulls": (
                "skulls",
                "usr",
                VIE_PURPLE,
                SKULLS_LDR_SKULLS_HEADER,
                SKULLS_LDR_USER_HEADER,
                SKULLS_LDR_HEADER,
            ),
        }

        (
            resource,
            table,
            colour,
            resource_header,
            user_header,
            leaderboard_header,
        ) = args_dict[leaderboard]

        starboard_ldr = await self.bot.pg_pool.fetch(
            f"SELECT usr_id, SUM({resource}) as total "
            f"FROM {table} "
            f"WHERE usr_id IN "
            f"(SELECT usr_id FROM usr WHERE guild_id = {interaction.guild.id}) "
            f"GROUP BY usr_id "
            f"ORDER BY total DESC ;"
        )

        embed = await build_leaderboard_embed(
            interaction,
            starboard_ldr,
            "total",
            "usr_id",
            colour,
            resource_header,
            user_header,
            leaderboard_header,
        )
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
                "https://cdn.discordapp.com/attachments/744224801429782679/805832792004755486/keiyb.png"
            )
            return

        await ensure_usr_existence(self.bot, recipient.id, recipient.guild.id)

        await self.bot.pg_pool.execute(
            f"UPDATE usr SET skulls = skulls + 1 WHERE usr_id = {recipient.id}"
        )
        await interaction.send(f"Gave a 💀 to {recipient.mention}")


async def build_leaderboard_embed(
    interaction,
    leaderboard,
    count_col_name,
    usr_col_name,
    color,
    header_count,
    header_user,
    header_title,
):

    if not leaderboard:
        return nextcord.Embed(color=color)
    ljust_num = len(str(header_count)) if str(header_count).isalnum() else 3
    ldr = []
    cnt = 0

    prev_count = -1
    keep_printing = True
    for rec in leaderboard:
        cnt += 1
        if cnt > MAX_LEADERBOARD_PRINT:
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

    header_merged = f"{header_count}\t{header_user}"

    merged_str = ""
    for line in ldr:
        merged_str += f"{line}\n"

    embed = nextcord.Embed(color=color)
    embed.add_field(name=header_merged, value=merged_str)
    embed.title = header_title
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
    link = user.avatar.url if user.avatar else ""
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
