import discord
import re
from settings import *
from utils.regex_fun_phrases import regex_fun_phrases_commands
from utils.regex_songs import regex_songs_commands
from utils.regex_uncategorized import regex_uncategorized_commands
from utils.regex_vftv import regex_vftv_commands
from utils.reputation import regex_reputation_command
from utils.regex_prio import regex_prio_commands


regex_commands = []
regex_commands.extend(regex_fun_phrases_commands)
regex_commands.extend(regex_songs_commands)
regex_commands.extend(regex_uncategorized_commands)

prio_commands = []
prio_commands.extend(regex_prio_commands)
prio_commands.extend(regex_reputation_command)


async def regex_handler(bot, message: discord.Message):

    if message.content.startswith(PREFIX):
        return

    for trig, resp, flags in prio_commands:
        if re.search(trig, message.content, flags) is not None:
            await resp(message)

    if message.channel.name in NO_RESPONSE_CHANNELS:
        return

    for trig, resp, flags in regex_commands:
        if re.search(trig, message.content, flags) is not None:
            await resp(message)

    if message.guild.id == GUILD_ID:
        for trig, resp, flags in regex_vftv_commands:
            if re.search(trig, message.content, flags) is not None:
                await resp(message)

