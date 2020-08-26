import discord
import re
import random
import asyncio
from cogs.admin import message_embed
from settings import *

regex_prio_commands = []


async def link_resp(message: discord.Message):
    ids = re.search(r"\d+\/\d+\/\d+", message.content).group()
    guild_id, channel_id, message_id = re.split(r"\/", ids)
    channel = discord.utils.get(message.guild.text_channels, id=int(channel_id))
    source_message = None

    try:
        source_message = await channel.fetch_message(int(message_id))
    except Exception:
        pass

    if not ((int(guild_id) == GUILD_ID) and channel and source_message):
        return

    embed = message_embed(source_message, "link", message.author)
    await message.channel.send(embed=embed)


regex_prio_commands.append(
    (r"https:\/\/discordapp\.com\/channels\/\d+\/\d+\/\d+", link_resp, re.M | re.I)
)
