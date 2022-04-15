import re
import nextcord
from db.db_func import ensure_usr_existence

regex_reputation_command = []

THANK_TYPE = "Void"


async def reputation_resp(bot, message: nextcord.Message):
    debugprint = ""
    debugprint += "debug: reputation start\n"
    if message:
        debugprint += f"debug: message {message}\ndebug: content: {message.content}\n"
    if message and message.mentions:
        debugprint += f"debug: message has thanks + mentions: {message.mentions}\n"
        for x in message.mentions:
            debugprint += "debug: starting for loop\n"
            if message.author.id == x.id:
                debugprint += "debug: message is a self-thank\n"
                await message.channel.send("Thanking yourself gives no reputation.")
                debugprint += "debug: self-thank message sent\n"
                continue
            debugprint += "debug: not a self-thank\n"
            await ensure_usr_existence(bot, x.id, x.guild.id)
            debugprint += "debug: existence ensured\n"
            await bot.pg_pool.execute(
                f"UPDATE usr SET thanks = thanks + 1 WHERE usr_id = {x.id}"
            )
            debugprint += "debug: DB command executed\n"
            await message.channel.send(f"Gave +1 {THANK_TYPE} to {x.mention}")
            debugprint += "debug: confirmation message sent\n"
    else:
        debugprint += "warn: thanks was triggered but not processed\n"
    print(debugprint, end="")


regex_reputation_command.append(
    (r"thanks?( (yo)?u)?( for .{2,60})?\W*<.{8,28}>", reputation_resp, re.M | re.I)
)
