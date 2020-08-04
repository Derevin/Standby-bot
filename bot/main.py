import os
import discord
from discord.ext import commands

from settings import *

bot = commands.Bot(command_prefix="+")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="PING DEREVIN IF BROKEN"))


for filename in os.listdir("bot/cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(BOT_TOKEN)
