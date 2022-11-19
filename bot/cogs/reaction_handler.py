import functools

from cogs.giveaways import giveaway_handler
from cogs.services import urban_handler
from nextcord.ext import commands
from utils.starboard import starboard_handler


class ReactionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def ignore_in_voice_channel(func):  # Deprecated
        @functools.wraps(func)
        async def wrapper(*args):
            bot = args[0].bot
            payload = args[1]
            channel = bot.get_channel(payload.channel_id)
            if not (channel and str(channel.type) == "voice"):
                await func(*args)

        return wrapper

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await starboard_handler(self.bot, payload)
        await giveaway_handler(self.bot, payload)
        # await role_handler(self.bot, payload)
        await urban_handler(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await starboard_handler(self.bot, payload)
        # await role_handler(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        await starboard_handler(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):
        await starboard_handler(self.bot, payload)


def setup(bot):
    bot.add_cog(ReactionHandler(bot))
