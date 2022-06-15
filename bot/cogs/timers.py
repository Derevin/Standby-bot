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
from db.db_func import ensure_guild_existence, ensured_get_usr


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

    @nextcord.slash_command(
        guild_ids=[GUILD_ID],
        description="Reminds you after a specified time",
    )
    async def remindme(
        self,
        interaction: Interaction,
        days: int = SlashOption(description="Days until the giveaway finishes"),
        hours: int = SlashOption(description="Hours until the giveaway finishes"),
        minutes: int = SlashOption(description="Minutes until the giveaway finishes"),
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

        await ensure_guild_existence(self.bot, interaction.guild.id)
        await ensured_get_usr(self.bot, interaction.user.id, interaction.guild.id)

        params_dict = {"msg": message, "channel": interaction.channel.id}
        params_json = json.dumps(params_dict)

        await self.bot.pg_pool.execute(
            "INSERT INTO tmers (usr_id, expires, ttype, params) VALUES ($1, $2, $3, $4);",
            interaction.user.id,
            tfuture,
            DB_TMER_REMINDER,
            params_json,
        )
        await interaction.send(
            f"{dynamic_timestamp(timenow, 'short')}: Your reminder has been registered "
            f"and you will be reminded on {dynamic_timestamp(tfuture, 'long')}."
        )


def setup(bot):
    bot.add_cog(Timers(bot))
