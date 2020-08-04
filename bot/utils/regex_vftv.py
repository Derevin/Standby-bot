import discord
import re
import random

regex_vftv_commands = []


async def pingsock_resp(message: discord.Message):
    if random.randint(1, 4) == 1:
        await message.channel.send(
            f"Do I see someone who loves being pinged, {message.author.mention}?"
        )


regex_vftv_commands.append(
    ("^<:Pingsock:421725383172554753>$", pingsock_resp, re.M | re.I)
)
