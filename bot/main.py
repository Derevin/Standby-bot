import os
import subprocess
import discord
import asyncio
import re
import traceback
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
    if channel:
        reason_found = "not found"
        try:
            logs = str(
                subprocess.check_output(
                    "heroku logs -n 15 --app=standby-bot", shell=True
                )
            )
            chunks = re.split("\\\\n", logs)
            next_is_reason = False
            for c in reversed(chunks):
                if next_is_reason:
                    reason_found = c.split("]: ")[1]
                    break
                if "State changed from up to" in c:
                    next_is_reason = True
                    continue
        except Exception:
            reason_found = "uknown"
            traceback.print_exc()
        await channel.send(f"Reboot complete. Reason:{reason_found}")


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
