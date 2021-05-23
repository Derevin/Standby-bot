import os
import discord
import asyncio
from discord.ext import commands
from settings import *

from db.db_main import init_db_connection

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Have a nice day!"))
    channel = bot.get_channel(ERROR_CHANNEL_ID)
    if channel:
        msg = await channel.send("Reboot complete.")
        await asyncio.sleep(180)
        await msg.delete()


for filename in os.listdir("bot/cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"cogs.{filename[:-3]}")

if not NODB:
    bot.loop.run_until_complete(init_db_connection(bot))
bot.run(BOT_TOKEN)
