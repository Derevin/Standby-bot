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
    "Claim this channel by typing: ```+topen```"
    " and then this channel will be restricted for your and mod-team eyes only.\n"
    "Disclamer: It is recommended to mute this channel's category,"
    " otherwise you will get an unread message notification "
    "everytime this channel gets recreated."
)
CLAIMED_MESSAGE = (
    "This channel has been claimed,"
    " you can make sure you're talking only to the mod team by looking "
    "at current member list of the channel (right side of discord)."
)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_claimable(self, cat):
        chnl = await cat.create_text_channel(
            name=CLAIMABLE_CHANNEL_NAME, reason="Making a claimable channel."
        )
        await chnl.send(CLAIMABLE_CHANNEL_MESSAGE)

    async def get_or_create_open_cat(self, ctx):
        open_ticket_cat = discord.utils.get(
            ctx.guild.categories, name=CLAIMABLE_TICKETS_CAT_NAME
        )
        if open_ticket_cat is None:
            open_ticket_cat = await ctx.guild.create_category(
                name=CLAIMABLE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return open_ticket_cat

    async def get_or_create_active_cat(self, ctx):
        active_ticket_cat = discord.utils.get(
            ctx.guild.categories, name=ACTIVE_TICKETS_CAT_NAME
        )
        if active_ticket_cat is None:
            active_ticket_cat = await ctx.guild.create_category(
                name=ACTIVE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return active_ticket_cat

    async def get_or_create_resolved_cat(self, ctx):
        resolved_ticket_cat = discord.utils.get(
            ctx.guild.categories, name=RESOLVED_TICKETS_CAT_NAME
        )
        if resolved_ticket_cat is None:
            resolved_ticket_cat = await ctx.guild.create_category(
                name=RESOLVED_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return resolved_ticket_cat

    async def get_highest_num(self, ctx):
        active_ticket_cat = await self.get_or_create_active_cat(ctx)
        resolved_ticket_cat = await self.get_or_create_resolved_cat(ctx)

        num = 0
        for x in active_ticket_cat.channels:
            lst = x.name.split("-")
            if int(lst[-1]) > num:
                num = int(lst[-1])

        for x in resolved_ticket_cat.channels:
            lst = x.name.split("-")
            if int(lst[-1]) > num:
                num = int(lst[-1])

        return num

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def tinit(self, ctx, *args):
        open_ticket_cat = await self.get_or_create_open_cat(ctx)
        if not open_ticket_cat.channels:
            await self.create_claimable(open_ticket_cat)

    @commands.command(aliases=["tclaim"])
    async def topen(self, ctx, *args):
        if ctx.channel.name != CLAIMABLE_CHANNEL_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a claimable channel"
            )
        issue_num = await self.get_highest_num(ctx) + 1
        print(issue_num)

        active_ticket_cat = await self.get_or_create_active_cat(ctx)
        await ctx.channel.edit(
            name=f"{ctx.author.name}-{issue_num}", category=active_ticket_cat
        )
        await ctx.channel.send(CLAIMED_MESSAGE)

        open_ticket_cat = await self.get_or_create_open_cat(ctx)
        if not open_ticket_cat.channels:
            await self.create_claimable(open_ticket_cat)

    @commands.command()
    async def treopen(self, ctx, *args):
        print("reopen")

    @commands.command()
    async def tresolve(self, ctx, *args):
        print("resolve")
        pass


def setup(bot):
    bot.add_cog(Tickets(bot))
