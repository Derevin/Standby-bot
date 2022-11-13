from nextcord.ext import commands, tasks, application_checks
import nextcord
from nextcord import Interaction, SlashOption
import asyncio
import random
import re
import datetime

from traitlets import default
from settings import *
from utils.util_functions import *

giveaway_lock = asyncio.Lock()


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @nextcord.slash_command(description="Start a giveaway in the #giveaways channel")
    # Set permissions manually
    async def giveaway(
        self,
        interaction: Interaction,
        days: int = SlashOption(description="Days until the giveaway finishes"),
        hours: int = SlashOption(description="Hours until the giveaway finishes"),
        minutes: int = SlashOption(description="Minutes until the giveaway finishes"),
        winners: int = SlashOption(description="Number of winners"),
        title: str = SlashOption(description="The title of your giveaway"),
    ):

        if days + hours + minutes == 0:
            await interaction.send(
                "Invalid time format, please try again", ephemeral=True
            )
            return

        now = nextcord.utils.utcnow()
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        end_time = now + delta
        embed = giveaway_embed(end_time, winners, interaction.user, title)
        giveaway_channel = nextcord.utils.get(
            interaction.guild.text_channels, name=GIVEAWAY_CHANNEL_NAME
        )
        giveaway = await giveaway_channel.send(embed=embed)
        await giveaway.add_reaction(TADA)
        await interaction.send(
            f"Giveaway started in {giveaway_channel.mention}! ", ephemeral=True
        )

    @nextcord.slash_command(
        description="Mod commands for editing giveaways",
        default_member_permissions=MODS_AND_GUIDES,
    )
    async def giveaway_tools(self, interaction):
        pass

    @giveaway_tools.subcommand(description="Manually end a giveaway")
    async def finish(
        self,
        interaction,
        id=SlashOption(
            description="ID of the giveaway (leave blank to use last active giveaway)",
            default=0,
        ),
    ):

        channel = get_channel(interaction.guild, GIVEAWAY_CHANNEL_NAME)

        if id != 0:
            try:
                giveaway = await channel.fetch_message(id)
                if is_active_giveaway(giveaway):
                    await finish_giveaway(giveaway)
                    await interaction.send("Giveaway finished", ephemeral=True)
            except Exception:
                await interaction.send(
                    "No active giveaway found with that ID", ephemeral=True
                )

        else:
            await giveaway_lock.acquire()
            try:
                async for message in channel.history(limit=50):
                    if is_active_giveaway(message):
                        await finish_giveaway(message)
                        await interaction.send("Giveaway finished", ephemeral=True)
                        return
            finally:
                giveaway_lock.release()

    @giveaway_tools.subcommand(description="Draw a new winner for a giveaway")
    async def redraw(
        self,
        interaction,
        number: int = SlashOption(description="number of winners to redraw"),
        id=SlashOption(
            description="ID of the giveaway (leave blank to use the last giveaway)",
            default=0,
        ),
    ):

        channel = get_channel(interaction.guild, GIVEAWAY_CHANNEL_NAME)
        giveaway = None

        if id == 0:
            async for message in channel.history():
                if (
                    message.embeds
                    and len(message.embeds[0].fields) >= 4
                    and message.embeds[0].fields[3].name == "Winner #1"
                ):
                    giveaway = message
                    break
        else:
            try:
                message = await channel.fetch_message(id)
                if (
                    message.embeds
                    and len(message.embeds[0].fields) >= 4
                    and message.embeds[0].fields[3].name == "Winner #1"
                ):
                    giveaway = message
                else:
                    await interaction.send(
                        "No finished giveaway found with that ID", ephemeral=True
                    )
                    return
            except Exception:
                await interaction.send("No message found with that ID", ephemeral=True)
                return

        if giveaway is not None:

            winners = []
            for field in giveaway.embeds[0].fields:
                if field.name.startswith("Winner") and field.value != "None":
                    winners.append(field.value)
            users = await who_reacted(giveaway, TADA)

            eligible = [user.mention for user in users if user.mention not in winners]

            if len(eligible) == 0:
                await giveaway.channel.send(
                    "All who entered the giveaway won a prize - there are no more names to draw from."
                )
                return
            else:
                if number > len(eligible):
                    if len(eligible) == 1:
                        await giveaway.channel.send(
                            "There is only 1 entrant left to draw from."
                        )
                    else:
                        await giveaway.channel.send(
                            f"There are only {len(eligible)} entrants left to draw from."
                        )
                    number = len(eligible)

                new_winners = random.sample(eligible, number)

            if len(new_winners) == 1:
                await giveaway.channel.send(
                    f"{TADA} The new winner is {new_winners[0]}! Congratulations!"
                )
            else:
                await giveaway.channel.send(
                    f"{TADA} The new winners are {', '.join(new_winners[:-1])} and {new_winners[-1]}! Congratulations!"
                )

            await interaction.send("Winner(s) successfully redrawn", ephemeral=True)

    @giveaway_tools.subcommand(description="Edits the number of winners for a giveaway")
    async def change(
        self,
        interaction,
        new_number: int = SlashOption(
            description="The number of winners the giveaway should have", min_value=1
        ),
        id=SlashOption(
            description="ID of the giveaway (leave blank to use the last giveaway)",
            default=0,
        ),
    ):

        channel = get_channel(interaction.guild, GIVEAWAY_CHANNEL_NAME)
        giveaway = None

        if id != 0:
            try:
                message = await channel.fetch_message(id)
                if is_finished_giveaway(message):
                    giveaway = message
                else:
                    await interaction.send(
                        "No finished giveaway found with that ID", ephemeral=True
                    )
                    return
            except Exception:
                await interaction.send("No message found with that ID", ephemeral=True)

        else:
            async for message in channel.history():
                if is_active_giveaway(message):
                    giveaway = message
                    break

        if giveaway is not None:
            embed = giveaway.embeds[0]
            text = embed.footer.text
            old_num = int(re.search(r"(\d+) winner", text).group(1))
            text = re.sub(r"(\d+) winner", f"{str(new_number)} winner", text)
            if old_num == 1:
                text = re.sub("winner", "winners", text)
            elif new_number == 1:
                text = re.sub("winners", "winner", text)
            embed.set_footer(text=text)
            await giveaway.edit(embed=embed)
            await interaction.send("Number of winners successfully changed")

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        guild = None

        try:
            guild = await self.bot.fetch_guild(GUILD_ID)
        except Exception:
            pass
        if guild:
            channels = await guild.fetch_channels()
            giveaway_channel = nextcord.utils.get(channels, name=GIVEAWAY_CHANNEL_NAME)
            if not giveaway_channel:
                return
            await giveaway_lock.acquire()
            try:
                async for message in giveaway_channel.history(limit=25):
                    if (
                        message.embeds
                        and len(message.embeds[0].fields) >= 3
                        and message.embeds[0].fields[2].name == "Time remaining"
                    ):
                        await update_giveaway(message)
            finally:
                giveaway_lock.release()


async def who_reacted(message, emoji):
    reactions = message.reactions
    users = []
    for reaction in reactions:
        if reaction.emoji == emoji:
            async for user in reaction.users():
                if user.id != BOT_ID:
                    users.append(user)
    return users


async def giveaway_handler(bot, payload):
    if isinstance(payload, nextcord.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if (
            payload.emoji.name == TADA
            and payload.user_id != BOT_ID
            and message.embeds
            and re.search("finished", message.embeds[0].description)
        ):
            await message.remove_reaction(TADA, payload.member)


async def update_giveaway(giveaway):
    embed = giveaway.embeds[0]
    end_time = embed.timestamp
    now = nextcord.utils.utcnow()
    delta = end_time - now
    if delta == datetime.timedelta(seconds=0) or delta.days < 0:
        await finish_giveaway(giveaway)
    else:
        embed.set_field_at(2, name="Time remaining", value=delta_to_text(delta))
        await giveaway.edit(embed=embed)


async def finish_giveaway(giveaway):

    embed = giveaway.embeds[0]
    embed.description = EMPTY + "\nThe giveaway has finished!\n" + EMPTY
    embed.set_field_at(1, name=EMPTY, value=EMPTY)
    embed.set_field_at(2, name=EMPTY, value=EMPTY)
    embed.set_footer(text=re.sub("Ends", "Ended", embed.footer.text))
    embed.timestamp = nextcord.utils.utcnow()

    num_winners = int(re.search("^(.+) winner", embed.footer.text).group(1))
    message = f"{giveaway.jump_url}\n"
    users = await who_reacted(giveaway, TADA)
    if len(users) == 0:
        message += "No winner could be determined."
    else:
        message += "Congratulations"
        if len(users) >= num_winners:
            winners = random.sample(users, num_winners)
        else:
            winners = users
            random.shuffle(winners)
        for winner in winners:
            embed.add_field(
                name=f"Winner #{winners.index(winner)+1}", value=winner.mention
            )
            message += f" {winner.mention}"
        for i in range(len(users), num_winners):
            embed.add_field(name=f"Winner #{i+1}", value="None")
        message += (
            f"!\nYou have won the {embed.title[8:-8].lower().strip()}!"
            + f"\nContact {embed.fields[0].value} for your prize."
        )

    await giveaway.edit(embed=embed)
    await giveaway.channel.send(message)


def is_active_giveaway(message):
    return (
        message.embeds
        and len(message.embeds[0].fields) >= 3
        and message.embeds[0].fields[2].name == "Time remaining"
    )


def is_finished_giveaway(message):
    return (
        message.embeds
        and len(message.embeds[0].fields) >= 4
        and message.embeds[0].fields[3].name == "Winner #1"
    )


def giveaway_embed(end_time, winners, author, title) -> nextcord.Embed:

    embed = nextcord.Embed(color=LIGHT_BLUE)
    embed.title = ":tada:**   " + title.upper() + " GIVEAWAY   **:tada:"
    now = nextcord.utils.utcnow()
    remaining = delta_to_text(end_time - now)
    embed.description = EMPTY + "\nReact with :tada: to enter!\n" + EMPTY

    winner_text = f"{winners} winner"
    if winners > 1:
        winner_text += "s"

    embed.set_footer(text=winner_text + "  •  Ends at")
    embed.timestamp = end_time
    embed.add_field(name="Hosted by", value=author.mention)
    embed.add_field(name=EMPTY, value=EMPTY)
    embed.add_field(name="Time remaining", value=remaining)
    embed.set_thumbnail(GIT_STATIC_URL + "/images/presents.png")
    return embed


def delta_to_text(delta) -> str:
    parts = []
    if delta.days != 0:
        day_text = f"**{delta.days}** day"
        if delta.days > 1:
            day_text += "s"
        parts.append(day_text)

    hours, seconds = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if hours > 0:
        hour_text = f"**{hours}** hour"
        if hours > 1:
            hour_text += "s"
        parts.append(hour_text)

    if minutes > 0:
        minute_text = f"**{minutes}** minute"
        if minutes > 1:
            minute_text += "s"
        parts.append(minute_text)

    if seconds > 0:
        second_text = f"**{seconds}** second"
        if seconds > 1:
            second_text += "s"
        parts.append(second_text)

    return ", ".join(parts)


def setup(bot):
    bot.add_cog(Giveaways(bot))
