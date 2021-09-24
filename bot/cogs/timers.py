from discord.ext import commands, tasks
import discord
import asyncio
import random
import re
import json
import sys
import traceback
from datetime import datetime, timedelta
from settings import *
from db.db_func import ensure_guild_existence, ensure_usr_existence


class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_timers.start()

    def cog_unload(self):
        self.check_timers.cancel()

    @tasks.loop(seconds=10)
    async def check_timers(self):
        try:
            gtable = await self.bot.pg_pool.fetch("SELECT * FROM tmers")
            for rec in gtable:
                if rec["ttype"] == DB_TMER_REMINDER:
                    timenow = datetime.now()
                    if timenow <= rec["expires"]:
                        continue

                    print(f"record expired: {rec}")
                    params_dict = json.loads(rec["params"])
                    if "msg" not in params_dict or "channel" not in params_dict:
                        print("invalid json, deleting")
                        await self.bot.pg_pool.execute(
                            "DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"]
                        )
                        continue
                    channel = self.bot.get_channel(params_dict["channel"])
                    if channel:
                        await channel.send(
                            f"<@{rec['usr_id']}> {rec['expires'].strftime('%b %d, %H:%M')}: {params_dict['msg']}"
                        )

                    await self.bot.pg_pool.execute(
                        "DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"]
                    )
                else:
                    print(f"type {rec['ttype']} is not yet implemented")
                    continue
        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return

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

        tdelta = timedelta(
            weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds
        )

        tfuture = timenow + tdelta

        await ensure_guild_existence(self.bot, ctx.guild.id)
        await ensure_usr_existence(self.bot, ctx.author.id, ctx.guild.id)

        joined = ""
        if msg:
            joined = " ".join(msg)
        params_dict = {"msg": joined, "channel": ctx.channel.id}
        params_json = json.dumps(params_dict)

        await self.bot.pg_pool.execute(
            "INSERT INTO tmers (usr_id, expires, ttype, params) VALUES ($1, $2, $3, $4);",
            ctx.author.id,
            tfuture,
            DB_TMER_REMINDER,
            params_json,
        )

        frmat = "%b %d, %H:%M" if timenow.year == tfuture.year else "%b %d %Y, %H:%M"
        await ctx.channel.send(
            f"{timenow.strftime('%b %d, %H:%M')} (bot time): Your reminder has been registered "
            f"and you will be reminded on {tfuture.strftime(frmat)}."
        )


def setup(bot):
    bot.add_cog(Timers(bot))
