import re
import discord
from db.db_func import ensure_usr_existence

regex_reputation_command = []

THANK_TYPE = "Void"


async def reputation_resp(bot, message: discord.Message):
    if message and message.mentions:
        for x in message.mentions:
            if message.author.id == x.id:
                await message.channel.send("Thanking yourself gives no reputation.")
                continue
            await ensure_usr_existence(bot, x.id, x.guild.id)
            await bot.pg_pool.execute(
                f"UPDATE usr SET thanks = thanks + 1 WHERE usr_id = {x.id}"
            )
            await message.channel.send(f"Gave +1 {THANK_TYPE} to {x.mention}")
    pass


regex_reputation_command.append(
    (r"thanks?( (yo)?u)?( for .{2,20})?\W*<@!.{14,22}>", reputation_resp, re.M | re.I)
)

