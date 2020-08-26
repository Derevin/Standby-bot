import discord
from discord.ext import commands
from utils.starboard import starboard_handler
from cogs.giveaways import giveaway_handler


class ReactionHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await starboard_handler(self.bot, payload)
        await giveaway_handler(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await starboard_handler(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload):
        await starboard_handler(self.bot, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload):
        await starboard_handler(self.bot, payload)


def setup(bot):
    bot.add_cog(ReactionHandler(bot))
