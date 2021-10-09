import os
import subprocess
import discord
import asyncio
import re
import aiohttp
from datetime import datetime, timedelta
from discord.ext import commands
from settings import *

from db.db_main import init_db_connection

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Have a nice day!"))
    channel = bot.get_channel(ERROR_CHANNEL_ID)
    if not channel:
        channel = bot.get_channel(740944936991457431)
    if channel:
        reason_found = "unkown reason"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://api.github.com/repos/Derevin/Standby-bot/commits/master"
            ) as r:
                data = await r.json()
                timenow = datetime.now()
                format = "%Y-%m-%dT%H:%M:%SZ"
                dt_commit_time = datetime.strptime(
                    data["commit"]["committer"]["date"], format
                )
                timepast = timenow - timedelta(minutes=5)
                if timepast < dt_commit_time:
                    author = data["commit"]["committer"]["name"]
                    message = data["commit"]["message"]
                    link = data["html_url"]
                    reason_found = (
                        f"commit from {author} with message `{message}`. Link: <{link}>"
                    )
                else:
                    reason_found = "Heroku restart or crash (most likely)."

        await channel.send(f"Reboot complete. Caused by {reason_found}")


#        await asyncio.sleep(180)
#        try:
#            await msg.delete()
#        except Exception:
#            pass


for filename in os.listdir("bot/cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"cogs.{filename[:-3]}")

if not NODB:
    bot.loop.run_until_complete(init_db_connection(bot))
bot.run(BOT_TOKEN)
