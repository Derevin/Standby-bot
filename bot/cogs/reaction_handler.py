from nextcord.ext.commands import Cog

from cogs.giveaways import giveaway_handler
from cogs.services import urban_handler
from utils.starboard import starboard_handler


class ReactionHandler(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await starboard_handler(self.bot, payload)
        await giveaway_handler(self.bot, payload)
        await urban_handler(self.bot, payload)


    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await starboard_handler(self.bot, payload)


    @Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        await starboard_handler(self.bot, payload)


    @Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):
        await starboard_handler(self.bot, payload)


def setup(bot):
    bot.add_cog(ReactionHandler(bot))
