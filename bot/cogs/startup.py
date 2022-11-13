import nextcord
from nextcord.ext import commands
from settings import *
import aiohttp
from utils.util_functions import *
from datetime import datetime, timedelta
import importlib
import json


class Startup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def load_cogs(bot):
    for filename in os.listdir("bot/cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            bot.load_extension(f"cogs.{filename[:-3]}")


async def set_status(bot, status):
    await bot.change_presence(activity=nextcord.Game(name=status))


async def log_restart_reason(bot):
    channel = bot.get_channel(ERROR_CHANNEL_ID)
    if not channel:
        channel = bot.get_channel(740944936991457431)
    if channel:
        reason_found = "unkown reason"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                "https://api.github.com/repos/Derevin/Standby-bot/commits/main"
            ) as r:
                data = await r.json()
                timenow = datetime.now().astimezone(BOT_TZ)
                format = "%Y-%m-%dT%H:%M:%S%z"
                dt_commit_time = datetime.strptime(
                    data["commit"]["committer"]["date"], format
                ).astimezone(BOT_TZ)
                timepast = timenow - timedelta(minutes=15)
                if timepast < dt_commit_time:
                    author = data["commit"]["committer"]["name"]
                    message = data["commit"]["message"]
                    link = data["html_url"]
                    reason_found = (
                        f"commit from {author} with message `{message}`. Link: <{link}>"
                    )
                else:
                    reason_found = "Heroku restart or crash."

        await channel.send(f"Reboot complete. Caused by {reason_found}")


async def reconnect_buttons(bot):

    guild = bot.get_guild(GUILD_ID)

    buttons = await bot.pg_pool.fetch(f"SELECT * FROM buttons")
    for button in buttons:
        try:
            channel = await bot.fetch_channel(button["channel_id"])
            message = await channel.fetch_message(button["message_id"])
            message.components[0]
        except (nextcord.errors.NotFound, IndexError):
            await bot.pg_pool.execute(
                f"DELETE from buttons WHERE channel_id = {button['channel_id']} AND message_id = {button['message_id']}"
            )
        else:
            all_disabled = True
            for component in message.components:
                for child in component.children:
                    if not child.disabled:
                        all_disabled = False
                        break
                else:
                    continue
                break

            if all_disabled:
                continue

            params = json.loads(button["params"]) if button["params"] else {}

            view = createView(button["type"], bot=bot, guild=guild, **params)
            await message.edit(view=view)


def createView(view_type, **params):

    package_name, view_name = view_type.split(" ")

    pkg = importlib.import_module(package_name)
    View = getattr(pkg, view_name)
    return View(**params)


def setup(bot):
    bot.add_cog(Startup(bot))
