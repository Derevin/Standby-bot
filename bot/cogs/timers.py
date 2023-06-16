import json
import sys
import traceback
from datetime import datetime as dt, timedelta

from nextcord import SlashOption, slash_command
from nextcord.ext.commands import Cog
from nextcord.ext.tasks import loop

from config.constants import *
from db_integration import db_functions as db
from utils import util_functions as uf


class Timers(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_timers.start()


    def cog_unload(self):
        self.check_timers.cancel()


    @loop(seconds=10)
    async def check_timers(self):
        try:
            gtable = await self.bot.pg_pool.fetch(f"SELECT * FROM tmers WHERE ttype={DB_TMER_REMINDER}")
            for rec in gtable:
                if rec["ttype"] == DB_TMER_REMINDER:
                    timenow = dt.now()
                    if timenow <= rec["expires"]:
                        continue

                    print(f"record expired: {rec}")
                    params_dict = json.loads(rec["params"])
                    if "msg" not in params_dict or "channel" not in params_dict:
                        print("invalid json, deleting")
                        await self.bot.pg_pool.execute("DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"])
                        continue
                    channel = self.bot.get_channel(params_dict["channel"])
                    if channel:
                        message = (f"<@{rec['usr_id']}> {uf.dynamic_timestamp(rec['expires'], 'long')}: "
                                   f"{params_dict['msg']}")
                        try:
                            confirmation_id = params_dict["confirmation_id"]
                            confirmation = await channel.fetch_message(confirmation_id)
                            message += " " + confirmation.jump_url
                        except Exception:
                            pass

                        await channel.send(message)

                    await self.bot.pg_pool.execute("DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"])
        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return


    @slash_command(description="Commands for setting reminders")
    async def remindme(self, interaction):
        pass


    @remindme.subcommand(description="Reminds you after a specified time", name="in")
    async def remindme_in(self, interaction,
                          days: int = SlashOption(description="Days until the reminder", min_value=0),
                          hours: int = SlashOption(description="Hours until the reminder", min_value=0),
                          minutes: int = SlashOption(description="Minutes until the reminder", min_value=0),
                          message=SlashOption(description="A message for the reminder")):
        if days + hours + minutes == 0:
            await interaction.send(ephemeral=True,
                                   file=uf.simpsons_error_image(dad=interaction.guild.me, son=interaction.user,
                                                                text="Invalid time format"))
            return

        now = dt.now()
        delta = timedelta(days=days, hours=hours, minutes=minutes)
        expires = now + delta
        expires = expires.replace(microsecond=0)

        confirmation = await interaction.send(f"{uf.dynamic_timestamp(now, 'short')}: Your reminder has been "
                                              "registered and you will be reminded "
                                              f"on {uf.dynamic_timestamp(expires, 'long')}.")
        full_confirmation = await confirmation.fetch()
        await create_reminder(self.bot, interaction, expires, message, full_confirmation.id)


    @remindme.subcommand(description="Reminds you at a specified date and time", name="at")
    async def remindme_at(self, interaction, year: int = SlashOption(description="Year of the reminder"),
                          month: int = SlashOption(description="Month of the reminder"),
                          day: int = SlashOption(description="Day of the reminder"),
                          hour: int = SlashOption(description="Hour of the reminder"),
                          minute: int = SlashOption(description="Minute of the reminder"),
                          message: str = SlashOption(description="A message for the reminder"), ):
        now = dt.now()
        try:
            expires = dt(year=year, month=month, day=day, hour=hour, minute=minute, tzinfo=now.tzinfo)
        except ValueError:
            await interaction.send("Please input a valid date and time.", ephemeral=True)
            return

        if expires < now:
            await interaction.send("You must choose a time that's in the future "
                                   f"(current bot time is {now.strftime('%H:%M')}).", ephemeral=True)
            return

        confirmation = await interaction.send(f"{uf.dynamic_timestamp(now, 'short')}: Your reminder has been "
                                              "registered and you will be reminded "
                                              f"on {uf.dynamic_timestamp(expires, 'long')}.")
        full_confirmation = await confirmation.fetch()
        await create_reminder(self.bot, interaction, expires, message, full_confirmation.id)


async def create_reminder(bot, interaction, tfuture, message, confirmation_id):
    await db.ensure_guild_existence(bot, interaction.guild.id)
    await db.get_or_insert_usr(bot, interaction.user.id, interaction.guild.id)

    params_dict = {"msg": message, "channel": interaction.channel.id, "confirmation_id": confirmation_id, }
    params_json = json.dumps(params_dict)

    await bot.pg_pool.execute("INSERT INTO tmers (usr_id, expires, ttype, params) VALUES ($1, $2, $3, $4);",
                              interaction.user.id, tfuture, DB_TMER_REMINDER, params_json, )


def setup(bot):
    bot.add_cog(Timers(bot))
