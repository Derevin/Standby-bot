from discord.ext import commands, tasks
import discord
import asyncio
import random
import re
from datetime import datetime, timedelta
from settings import *
from db.db_func import ensure_guild_existence, ensure_usr_existence


class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10)
    async def check_timers(self):
        pass

    @commands.command(
        aliases=["remind", "reminder", "notifyme"],
        brief="Reminds you after a specified time",
    )
    async def remindme(self, ctx, time, *msg):

        if not re.search(r"(\d+[wdhms])+", time):
            raise commands.errors.BadArgument("Invalid time format")

        weeks = re.search(r"(\d+)w", time)
        weeks = int(weeks.group(1)) if weeks else 0
        days = re.search(r"(\d+)d", time)
        days = int(days.group(1)) if days else 0
        hours = re.search(r"(\d+)h", time)
        hours = int(hours.group(1)) if hours else 0
        minutes = re.search(r"(\d+)m", time)
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = re.search(r"(\d+)s", time)
        seconds = int(seconds.group(1)) if seconds else 0
        if weeks + days + hours + minutes + seconds == 0:
            raise commands.errors.BadArgument("Invalid time format")

        timenow = datetime.now()

        timefuture = timedelta(
            weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
        )

        await ensure_guild_existence(self.bot, ctx.guild.id)
        await ensure_usr_existence(self.bot, ctx.author.id, ctx.guild.id)

        await ctx.channel.send(
            f"(Not yet functional) Your reminder has been registered on {timenow} (bot time) "
            f"and you will be reminded on {timenow + timefuture} (bot time)."
        )


def setup(bot):
    bot.add_cog(Timers(bot))
