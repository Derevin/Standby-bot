import datetime
from discord.ext import commands, timers, tasks
import discord
import asyncio
import time
from cogs.giveaways import update_giveaway
from settings import *


class TimeHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=5)
    async def check_giveaways(self):
        guild = None

        try:
            guild = await self.bot.fetch_guild(GUILD_ID)
        except Exception:
            pass
        if guild:
            channels = await guild.fetch_channels()
            giveaway_channel = discord.utils.get(channels, name=GIVEAWAY_CHANNEL_NAME)
            async for message in giveaway_channel.history():
                if (
                    message.embeds
                    and len(message.embeds[0].fields) >= 3
                    and message.embeds[0].fields[2].name == "Time remaining"
                ):
                    await update_giveaway(message)


def setup(bot):
    bot.add_cog(TimeHandler(bot))
