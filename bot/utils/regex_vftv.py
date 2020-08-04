import discord
import re

regex_vftv_commands = []


async def pingsock_resp(message: discord.Message):
    pass


regex_vftv_commands.append(
    ("^<:Pingsock:421725383172554753>$", pingsock_resp, re.M | re.I)
)

regex_vftv_commands.append(
    ("^<:Pingsock:421725383172554753>$", pingsock_resp, re.M | re.I)
)
