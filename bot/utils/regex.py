import nextcord
import re
import datetime
from settings import *
from utils.regex_fun_phrases import regex_fun_phrases_commands
from utils.regex_songs import regex_songs_commands
from utils.regex_uncategorized import regex_uncategorized_commands
from utils.regex_vftv import regex_vftv_commands
from utils.reputation import regex_reputation_command
from utils.regex_prio import regex_prio_commands
from utils.regex_wednesday import languages

regex_commands = []
regex_commands.extend(regex_fun_phrases_commands)
regex_commands.extend(regex_songs_commands)
regex_commands.extend(regex_uncategorized_commands)

prio_commands = []
prio_commands.extend(regex_prio_commands)

prio_db_commands = []
prio_db_commands.extend(regex_reputation_command)


async def handle_commands(bot, message: nextcord.Message, cmnds):
    for trig, resp, flags in cmnds:
        if re.search(trig, message.content, flags) is not None:
            await resp(bot, message)


async def handle_wednesday_commands(bot, message):
    for lang in languages.values():
        if re.search(
            "^.{0,4}" + lang.trigger + "\\W{0,4}$", message.content, re.M | re.I
        ):
            if datetime.datetime.now().weekday() == lang.trigger_day:
                await message.channel.send(lang.response)
                await message.channel.send(lang.scream)
            else:
                await message.channel.send(lang.wrong_day)


async def regex_handler(bot, message: nextcord.Message):

    await handle_commands(bot, message, prio_commands)
    await handle_commands(bot, message, prio_db_commands)

    if message.channel.name in NO_RESPONSE_CHANNELS:
        return

    await handle_commands(bot, message, regex_commands)
    await handle_wednesday_commands(bot, message)

    if message.guild.id == GUILD_ID:
        await handle_commands(bot, message, regex_vftv_commands)
