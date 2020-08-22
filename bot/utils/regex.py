import discord
import re
from settings import *
from utils.regex_fun_phrases import regex_fun_phrases_commands
from utils.regex_songs import regex_songs_commands
from utils.regex_uncategorized import regex_uncategorized_commands
from utils.regex_vftv import regex_vftv_commands
from utils.reputation import regex_reputation_command


regex_commands = []
regex_commands.extend(regex_fun_phrases_commands)
regex_commands.extend(regex_songs_commands)
regex_commands.extend(regex_uncategorized_commands)


async def regex_handler(bot, message: discord.Message):
    for c in NO_RESPONSE_CHANNELS:
        if message.channel.name == c:
            return
    for trig, resp, flags in regex_commands:
        if re.search(trig, message.content, flags) is not None:
            await resp(message)
    for trig, resp, flags in regex_reputation_command:
        if re.search(trig, message.content, flags) is not None:
            await resp(bot, message)
    if message.guild.id == GUILD_ID:
        for trig, resp, flags in regex_vftv_commands:
            if re.search(trig, message.content, flags) is not None:
                await resp(message)

