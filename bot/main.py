import os
import subprocess
import nextcord
import asyncio
import re
import aiohttp
from datetime import datetime, timedelta
from nextcord.ext import commands

from settings import *

from db.db_main import init_db_connection

from cogs.startup import *

intents = nextcord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

bot = commands.Bot(intents=intents, case_insensitive=True)


@bot.event
async def on_ready():

    await set_status(bot, "Have a nice day!")

    await log_restart_reason(bot)

    await reconnect_buttons(bot)


load_cogs(bot)

bot.loop.run_until_complete(init_db_connection(bot))

bot.run(BOT_TOKEN)
