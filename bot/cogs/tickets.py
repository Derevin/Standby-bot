from discord.ext import commands
import discord
from settings import *
from inspect import Parameter


CLAIMABLE_TICKETS_CAT_NAME = "Talk to mods"
CLAIMABLE_CHANNEL_NAME = "claim-this-channel"
ACTIVE_TICKETS_CAT_NAME = "Active tickets"
RESOLVED_TICKETS_CAT_NAME = "Resolved tickets"
CLAIMABLE_CHANNEL_MESSAGE = (
    "If you want to talk to the mod team, this is the place!\n"
    "Claim this channel by typing ```+topen```"
    " and then this channel will be restricted for your and mod-team eyes only\n"
    "Disclamer: It is recommended to mute this channel's category,"
    " otherwise you will get an unread message notification "
    "everytime this channel get recreated"
)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_claimable(self, cat):
        chnl = await cat.create_text_channel(
            name=CLAIMABLE_CHANNEL_NAME, reason="Making a claimable channel."
        )
        await chnl.send(CLAIMABLE_CHANNEL_MESSAGE)

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def tinit(self, ctx, *args):
        print(ctx.guild.categories)
        open_ticket_cat = discord.utils.get(
            ctx.guild.categories, name=CLAIMABLE_TICKETS_CAT_NAME
        )
        if open_ticket_cat is None:
            open_ticket_cat = await ctx.guild.create_category(
                name=CLAIMABLE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        print(open_ticket_cat.channels)
        if not open_ticket_cat.channels:
            await self.create_claimable(open_ticket_cat)

    @commands.command(aliases=["tclaim"])
    async def topen(self, ctx, *args):
        if ctx.channel.name != CLAIMABLE_CHANNEL_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a claimable channel"
            )
        print("open")
        pass

    @commands.command()
    async def treopen(self, ctx, *args):
        print("reopen")
        pass

    @commands.command()
    async def tresolve(self, ctx, *args):
        print("resolve")
        pass


def setup(bot):
    bot.add_cog(Tickets(bot))
