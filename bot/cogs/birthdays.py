from nextcord.ext import commands, tasks
import nextcord
import datetime
from settings import *
from utils.util_functions import *
import json
from db.db_func import ensure_guild_existence, ensure_usr_existence


class Birthdays(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_bdays.start()

    def cog_unload(self):
        pass
        self.check_bdays.cancel()

    @commands.group(brief="Birthday commands", aliases=["bday"])
    async def birthday(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Type `+help birthday` to see available subcommands.")

    @birthday.command(brief="Set your birthday")
    async def set(self, ctx, day, month):

        await ctx.message.delete()

        months = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]

        try:

            day = int(day)

            if month[:3] in months:
                month = months.index(month[:3]) + 1
            else:
                month = int(month)

        except Exception:
            day = 32
            month = 13

        if not (month <= 12 and day <= 31):
            await ctx.send("Invalid date - please try again.")
            return

        await ensure_guild_existence(self.bot, ctx.guild.id)
        await ensure_usr_existence(self.bot, ctx.author.id, ctx.guild.id)

        exists = await self.bot.pg_pool.fetch(
            f"SELECT * FROM bdays WHERE usr_id = {ctx.author.id}"
        )

        if exists:
            await self.bot.pg_pool.execute(
                f"""UPDATE bdays SET month = {month}, day = {day} WHERE usr_id = {ctx.author.id}"""
            )
        else:
            await self.bot.pg_pool.execute(
                """INSERT INTO bdays (usr_id, month, day) """
                """VALUES ($1, $2, $3);""",
                ctx.author.id,
                month,
                day,
            )

        await ctx.send("Your birthday has been set.")

    @birthday.command(brief="Remove your birthday", aliases=["clear"])
    async def remove(self, ctx):

        exists = await self.bot.pg_pool.fetch(
            f"SELECT * FROM bdays WHERE usr_id = {ctx.author.id}"
        )
        if not exists:
            await ctx.send("You have not set your birthday.")
        else:
            await self.bot.pg_pool.execute(
                f"DELETE FROM bdays WHERE usr_id = {ctx.author.id};"
            )
            await ctx.send("Birthday removed.")

    @tasks.loop(hours=1)
    async def check_bdays(self):

        now = nextcord.utils.utcnow()

        if now.hour != 7:
            return

        await self.bot.wait_until_ready()

        guild = await self.bot.fetch_guild(GUILD_ID)

        bday_role = get_role(guild, BIRTHDAY_NAME)

        async for member in guild.fetch_members():
            if bday_role in member.roles:
                await member.remove_roles(bday_role)

        gtable = await self.bot.pg_pool.fetch(
            f"SELECT * FROM bdays WHERE month = {now.month} AND day = {now.day}"
        )

        if not gtable:
            return

        bday_havers = []

        for rec in gtable:

            member = await guild.fetch_member(rec["usr_id"])

            await member.add_roles(bday_role)

            bday_havers.append(member.mention)

        if len(bday_havers) > 1:
            txt = ", ".join(bday_havers[:-1]) + " and " + str(bday_havers[-1])
        else:
            txt = bday_havers[0]
        print(txt)
        general = nextcord.utils.get(self.bot.get_all_channels(), name="general")
        await general.send("🎂🎂🎂")
        await general.send("Happy Birthday " + txt + "!")


def setup(bot):
    bot.add_cog(Birthdays(bot))
