import nextcord.utils
from nextcord import SlashOption, slash_command
from nextcord.ext.commands import Cog
from nextcord.ext.tasks import loop

from config.constants import *
from db_integration import db_functions as db
from utils import util_functions as uf


class Birthdays(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_bdays.start()


    def cog_unload(self):
        pass
        self.check_bdays.cancel()


    @slash_command(description="Commands for accessing birthday functionality")
    async def birthday(self, interaction):
        pass


    @birthday.subcommand(description="Set your birthday")
    async def set(self, interaction, month_name: str = SlashOption(name="month", description="Your birth month",
                                                                   choices=["January", "February", "March", "April",
                                                                           "May", "June", "July", "August", "September",
                                                                           "October", "November", "December"]),
                  day: int = SlashOption(min_value=1, max_value=31, description="Your birth date")):
        month = uf.month_to_int(month_name)
        if (month in [2, 4, 6, 9, 11] and day == 31) or (month == 2 and day > 29):
            await interaction.send("Invalid date - please try again.", ephemeral=True)
            return

        await db.ensure_guild_existence(self.bot, interaction.guild.id)
        await db.get_or_insert_usr(self.bot, interaction.user.id, interaction.guild.id)

        exists = await self.bot.pg_pool.fetch(f"SELECT * FROM bdays WHERE usr_id = {interaction.user.id}")

        if exists:
            await self.bot.pg_pool.execute(
                    f"UPDATE bdays SET month = {month}, day = {day} WHERE usr_id = {interaction.user.id}")
        else:
            await self.bot.pg_pool.execute("INSERT INTO bdays (usr_id, month, day) VALUES ($1, $2, $3);",
                                           interaction.user.id, month, day)

        await interaction.send("Your birthday has been set.", ephemeral=True)


    @birthday.subcommand(description="Remove your birthday")
    async def remove(self, interaction):

        exists = await self.bot.pg_pool.fetch(f"SELECT * FROM bdays WHERE usr_id = {interaction.user.id}")
        if not exists:
            await interaction.send("You have not set your birthday.", ephemeral=True)
        else:
            await self.bot.pg_pool.execute(f"DELETE FROM bdays WHERE usr_id = {interaction.user.id};")
            await interaction.send("Birthday removed.", ephemeral=True)


    @birthday.subcommand(description="Check your birthday (only visible to you)")
    async def check(self, interaction):

        exists = await self.bot.pg_pool.fetch(f"SELECT * FROM bdays WHERE usr_id = {interaction.user.id}")
        if not exists:
            await interaction.send("You have not set your birthday.", ephemeral=True)
        else:
            await interaction.send(f"Your birthday is set to {uf.int_to_month(exists[0]['month'])} {exists[0]['day']}.",
                                   ephemeral=True)


    @loop(hours=1)
    async def check_bdays(self):

        now = uf.utcnow()

        if now.hour != 7:
            return

        await self.bot.wait_until_ready()

        guild = await self.bot.fetch_guild(GUILD_ID)

        bday_role = uf.get_role(guild, BIRTHDAY_NAME)

        async for member in guild.fetch_members():
            if bday_role in member.roles:
                await member.remove_roles(bday_role)

        gtable = await self.bot.pg_pool.fetch(f"SELECT * FROM bdays WHERE month = {now.month} AND day = {now.day}")

        if not gtable:
            return

        bday_havers = []

        for rec in gtable:
            member = await guild.fetch_member(rec["usr_id"])

            await member.add_roles(bday_role)

            bday_havers.append(member.mention)

        if len(bday_havers) > 1:
            bday_havers = ", ".join(bday_havers[:-1]) + " and " + str(bday_havers[-1])
        else:
            bday_havers = bday_havers[0]
        general = nextcord.utils.get(self.bot.get_all_channels(), name="general")
        await general.send("🎂🎂🎂")
        await general.send(f"Happy Birthday {bday_havers}!")


def setup(bot):
    bot.add_cog(Birthdays(bot))
