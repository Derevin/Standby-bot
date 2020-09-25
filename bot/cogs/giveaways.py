from discord.ext import commands, tasks
import discord
import asyncio
import random
import re
import datetime
from settings import *

giveaway_lock = asyncio.Lock()


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @commands.command(brief="Starts a giveaway in the #giveaways channel")
    @commands.has_any_role("Moderator", "Guides of the Void", "Raffler")
    async def gstart(self, ctx, time, winners, *title):

        await ctx.message.delete()

        if not re.search(r"(\d+[dhms])+", time):
            raise commands.errors.BadArgument("Invalid time format")
        if not re.search(r"^([1-9]\d*)w?$", winners):
            raise commands.errors.BadArgument("Invalid winner format")

        days = re.search(r"(\d+)d", time)
        days = int(days.group(1)) if days else 0
        hours = re.search(r"(\d+)h", time)
        hours = int(hours.group(1)) if hours else 0
        minutes = re.search(r"(\d+)m", time)
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = re.search(r"(\d+)s", time)
        seconds = int(seconds.group(1)) if seconds else 0
        if days + hours + minutes + seconds == 0:
            raise commands.errors.BadArgument("Invalid time format")

        num_winners = int(re.search(r"^(\d+)w?$", winners).group(1))

        title = " ".join(title)

        now = datetime.datetime.utcnow()
        delta = datetime.timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )
        end_time = now + delta
        embed = giveaway_embed(end_time, num_winners, ctx.author, title)
        giveaway_channel = discord.utils.get(
            ctx.guild.text_channels, name=GIVEAWAY_CHANNEL_NAME
        )
        giveaway = await giveaway_channel.send(embed=embed)
        await giveaway.add_reaction(TADA)

    @commands.command(brief="Manually end a giveaway")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def gfinish(self, ctx, id=None):

        await ctx.message.delete()

        channel = discord.utils.get(ctx.guild.text_channels, name=GIVEAWAY_CHANNEL_NAME)

        if id:
            id = "".join(id)
            try:
                giveaway = await channel.fetch_message(id)
                if is_active_giveaway(giveaway):
                    await finish_giveaway(giveaway)
            except Exception:
                raise commands.errors.BadArgument(
                    "No active giveaway found with that ID"
                )

        else:
            await giveaway_lock.acquire()
            try:
                async for message in channel.history(limit=50):
                    if is_active_giveaway(message):
                        await finish_giveaway(message)
                        return
            finally:
                giveaway_lock.release()

    @commands.command(brief="Draw a new winner for a giveaway", aliases=["greroll"])
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def gredraw(self, ctx, number=1, id="last"):

        await ctx.message.delete()

        number = int(number)
        if number > 1000:
            if id == "last":
                id = number
                number = 1
            else:
                number, id = int(id), number

        channel = discord.utils.get(ctx.guild.text_channels, name=GIVEAWAY_CHANNEL_NAME)
        giveaway = None

        if id == "last":
            async for message in channel.history():
                if (
                    message.embeds
                    and len(message.embeds[0].fields) >= 4
                    and message.embeds[0].fields[3].name == "Winner #1"
                ):
                    giveaway = message
                    break
        else:
            id = int(id)
            try:
                message = await channel.fetch_message(id)
                if (
                    message.embeds
                    and len(message.embeds[0].fields) >= 4
                    and message.embeds[0].fields[3].name == "Winner #1"
                ):
                    giveaway = message
                else:
                    raise commands.errors.BadArgument(
                        "No finished giveaway found with that ID"
                    )
            except Exception:
                raise commands.errors.BadArgument("No message found with that ID")

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

    @commands.command(brief="Edits the number of winners for a giveaway")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def gchange(self, ctx, change, *id):

        await ctx.message.delete()

        channel = discord.utils.get(ctx.guild.text_channels, name=GIVEAWAY_CHANNEL_NAME)
        giveaway = None

        if id:
            id = "".join(id)
            try:
                message = await channel.fetch_message(id)
                if is_finished_giveaway(message):
                    giveaway = message
                else:
                    raise commands.errors.BadArgument(
                        "No finished giveaway found with that ID"
                    )
            except Exception:
                raise commands.errors.BadArgument("No message found with that ID")

        else:
            async for message in channel.history():
                if is_active_giveaway(message):
                    giveaway = message
                    break

        if giveaway is not None:
            embed = giveaway.embeds[0]
            text = embed.footer.text
            old_num = int(re.search(r"(\d+) winner", text).group(1))
            new_num = old_num + int(change)
            if new_num < 1:
                raise commands.errors.BadArgument("Must have at least 1 winner")
            text = re.sub(r"(\d+) winner", f"{str(new_num)} winner", text)
            if old_num == 1:
                text = re.sub("winner", "winners", text)
            elif new_num == 1:
                text = re.sub("winners", "winner", text)
            embed.set_footer(text=text)
            await giveaway.edit(embed=embed)

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        guild = None

        try:
            guild = await self.bot.fetch_guild(GUILD_ID)
        except Exception:
            pass
        if guild:
            channels = await guild.fetch_channels()
            giveaway_channel = discord.utils.get(channels, name=GIVEAWAY_CHANNEL_NAME)
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
    if isinstance(payload, discord.RawReactionActionEvent):
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
    now = datetime.datetime.utcnow()
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
    embed.timestamp = datetime.datetime.utcnow()

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


def giveaway_embed(end_time, winners, author, title) -> discord.Embed:

    embed = discord.Embed(color=LIGHT_BLUE)
    embed.title = ":tada:**   " + title.upper() + " GIVEAWAY   **:tada:"
    now = datetime.datetime.utcnow()
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
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/744224801429782679/747945291130601603/presents.png"
    )
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

