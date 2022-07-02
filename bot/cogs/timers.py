from nextcord.ext import commands, tasks
import nextcord
from nextcord import Interaction, SlashOption
import asyncio
import random
import re
import json
import sys
import traceback
from datetime import datetime, timedelta
from utils.util_functions import dynamic_timestamp
from settings import *
from db.db_func import ensure_guild_existence, get_or_insert_usr


class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_timers.start()

    def cog_unload(self):
        self.check_timers.cancel()

    @tasks.loop(seconds=10)
    async def check_timers(self):
        try:
            gtable = await self.bot.pg_pool.fetch(
                f"SELECT * FROM tmers WHERE ttype={DB_TMER_REMINDER}"
            )
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
                            f"<@{rec['usr_id']}> {dynamic_timestamp(rec['expires'],'long')}: {params_dict['msg']}"
                        )

                    await self.bot.pg_pool.execute(
                        "DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"]
                    )
        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return

    @nextcord.slash_command(description="Commands for setting reminders")
    async def remindme():
        pass

    @remindme.subcommand(description="Reminds you after a specified time", name="in")
    async def remindme_in(
        self,
        interaction: Interaction,
        days: int = SlashOption(description="Days until the reminder", min_value=0),
        hours: int = SlashOption(description="Hours until the reminder", min_value=0),
        minutes: int = SlashOption(description="Minutes until the reminder", min_value=0),  # fmt: skip
        message=SlashOption(description="A message for the reminder"),
    ):

        if days + hours + minutes == 0:
            await interaction.send("Invalid time format", ephemeral=True)
            return

        timenow = datetime.now()

        tdelta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
        )

        tfuture = timenow + tdelta
        tfuture = tfuture.replace(microsecond=0)

        await create_reminder(self.bot, interaction, tfuture, message)

        await interaction.send(
            f"{dynamic_timestamp(timenow, 'short')}: Your reminder has been registered "
            f"and you will be reminded on {dynamic_timestamp(tfuture, 'long')}."
        )

    @remindme.subcommand(
        description="Reminds you at a specified date and time", name="at"
    )
    async def remindme_at(
        self,
        interaction: Interaction,
        year: int = SlashOption(description="Year of the reminder"),
        month: int = SlashOption(description="Month of the reminder"),
        day: int = SlashOption(description="Day of the reminder"),
        hour: int = SlashOption(description="Hour of the reminder"),
        minute: int = SlashOption(description="Minute of the reminder"),
        message: str = SlashOption(description="A message for the reminder"),
    ):
        timenow = datetime.now()
        try:
            tfuture = datetime(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                tzinfo=timenow.tzinfo,
            )
        except ValueError:
            await interaction.send(
                "Please input a valid date and time.", ephemeral=True
            )
            return

        if tfuture < timenow:
            await interaction.send(
                f"You must choose a time that's in the future (current bot time is {timenow.strftime('%H:%M')}).",
                ephemeral=True,
            )
            return

        await create_reminder(self.bot, interaction, tfuture, message)

        await interaction.send(
            f"{dynamic_timestamp(timenow, 'short')}: Your reminder has been registered "
            f"and you will be reminded on {dynamic_timestamp(tfuture, 'long')}."
        )


async def create_reminder(bot, interaction, tfuture, message):

    await ensure_guild_existence(bot, interaction.guild.id)
    await get_or_insert_usr(bot, interaction.user.id, interaction.guild.id)

    params_dict = {"msg": message, "channel": interaction.channel.id}
    params_json = json.dumps(params_dict)

    await bot.pg_pool.execute(
        "INSERT INTO tmers (usr_id, expires, ttype, params) VALUES ($1, $2, $3, $4);",
        interaction.user.id,
        tfuture,
        DB_TMER_REMINDER,
        params_json,
    )


def setup(bot):
    bot.add_cog(Timers(bot))
