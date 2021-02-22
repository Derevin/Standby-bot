import re
import discord
from db.db_func import ensure_usr_existence

regex_reputation_command = []

THANK_TYPE = "Void"


async def reputation_resp(bot, message: discord.Message):
    if message and message.mentions:
        print("debug: message has thanks + mention")
        for x in message.mentions:
            print("debug: starting for loop")
            if message.author.id == x.id:
                print("debug: message is a self-thank")
                await message.channel.send("Thanking yourself gives no reputation.")
                print("debug: self-thank message sent")
                continue
            print("debug: not a self-thank")
            await ensure_usr_existence(bot, x.id, x.guild.id)
            print("debug: existence ensured")
            await bot.pg_pool.execute(
                f"UPDATE usr SET thanks = thanks + 1 WHERE usr_id = {x.id}"
            )
            print("debug: DB command executed")
            await message.channel.send(f"Gave +1 {THANK_TYPE} to {x.mention}")
            print("debug: confirmation message sent")
    pass


regex_reputation_command.append(
    (r"thanks?( (yo)?u)?( for .{2,20})?\W*<@!.{14,22}>", reputation_resp, re.M | re.I)
)

