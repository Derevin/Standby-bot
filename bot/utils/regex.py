import discord
import re
from settings import *
from utils.regex_songs import regex_songs_commands
from utils.regex_uncategorized import regex_uncategorized_commands
from utils.regex_vftv import regex_vftv_commands


regex_commands = []
regex_commands.extend(regex_songs_commands)
regex_commands.extend(regex_uncategorized_commands)


async def regex_handler(message: discord.Message):
    for trig, resp, flags in regex_commands:
        if re.search(trig, message.content, flags) is not None:
            await resp(message)
    if message.guild.id == GUILD_ID:
        for trig, resp, flags in regex_vftv_commands:
            if re.search(trig, message.content, flags) is not None:
                await resp(message)


############ ayaya regex


async def ayaya_resp(message: discord.Message):
    await message.channel.send("Ayaya!")
    if message.guild.id == GUILD_ID:
        await message.add_reaction(":Ayy:610479153937907733")
        await message.add_reaction(":Ayy2:470743166207787010")


regex_commands.append(("^ayaya\\W{0,4}$", ayaya_resp, re.M | re.I))


############ test regex


async def test_resp(message: discord.Message):
    await message.channel.send("Ayaaaaaaaaaaaa!")


regex_commands.append(("^testtest$", test_resp, re.M | re.I))
