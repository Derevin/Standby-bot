from nextcord import Intents
from nextcord.ext.commands import Bot

from config import startup
from config.constants import BOT_TOKEN
from db_integration import db_functions as db

intents = Intents.all()
bot = Bot(intents=intents, case_insensitive=True)


@bot.event
async def on_ready():
    await startup.set_status(bot, "Have a nice day!")

    await startup.log_restart_reason(bot)

    await startup.reconnect_buttons(bot)


startup.load_cogs(bot)

bot.loop.run_until_complete(db.init_connection(bot))

bot.run(BOT_TOKEN)
