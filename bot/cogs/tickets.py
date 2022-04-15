from nextcord.ext import commands
import nextcord
from cogs.error_handler import unhandled_error_embed
from settings import *
from inspect import Parameter


CLAIMABLE_TICKETS_CAT_NAME = "Talk to mods"
CLAIMABLE_CHANNEL_NAME = "claim-this-channel"
ACTIVE_TICKETS_CAT_NAME = "Active tickets"
RESOLVED_TICKETS_CAT_NAME = "Resolved tickets"
TICKETS_LOG_CHANNEL_NAME = "tickets-log"
CLAIMABLE_CHANNEL_MESSAGE = (
    "If you have an issue and want to talk to the mod team, this is the place!\n"
    "Claim this channel by typing: ```+ticket claim```"
    " and then this channel will be restricted for your and mod-team eyes only.\n"
    "Disclaimer: It is recommended to mute this channel's category,"
    " otherwise you will get an unread message notification "
    "everytime this channel gets recreated."
)
CLAIMED_MESSAGE = (
    "You have successfully claimed this channel, please type what is it that you want to discuss.\n"
    "You can make sure you're talking only to the mod team by looking "
    "at current member list of the channel (right side of discord).\n"
    "Once this issue has been resolved, type: ```+ticket resolve```"
)

RESOLVED_MESSAGE = (
    "This issue has been marked as resolved."
    " If this was a mistake, type: ```+ticket reopen``` otherwise open a new issue.\n"
    "This issue can be scrapped with ```+ticket scrap``` by moderators.\n"
    "Scrapping takes a while to complete."
)

REOPENED_MESSAGE = "This issue has been reopened. Once the issue is resolved, type: ```+ticket resolve```"


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return
        if (
            str(message.channel.type) == "text"
            and str(message.channel.name) == CLAIMABLE_CHANNEL_NAME
        ):
            try:
                await message.delete()
            except Exception as e:
                channel = nextcord.utils.get(
                    message.guild.text_channels, name=ERROR_CHANNEL_NAME
                )
                if channel is not None:
                    await channel.send(
                        embed=unhandled_error_embed(message.content, message.channel, e)
                    )

    @commands.group(brief="Ticketing system, see subhelp for further commands")
    async def ticket(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid ticket subcommand passed...")

    @ticket.command(brief="Initiates ticket system - creates categories, channels etc")
    @commands.has_any_role(*MOD_ROLES)
    async def init(self, ctx, *args):
        claimable_ticket_cat = await self.get_or_create_claimable_cat(ctx)
        if not claimable_ticket_cat.channels:
            await self.create_claimable_channel(claimable_ticket_cat)
        await self.get_or_create_active_cat(ctx)
        await self.get_or_create_resolved_cat(ctx)
        await self.get_or_create_tickets_log(ctx)

    @ticket.command(aliases=["open"], brief="Claims the ticket channel")
    async def claim(self, ctx, *args):
        if ctx.channel.name != CLAIMABLE_CHANNEL_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a claimable channel"
            )

        issue_num = await self.get_highest_num(ctx) + 1

        active_ticket_cat = await self.get_or_create_active_cat(ctx)
        overwrites = {
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
        }

        ticket_chnl = await active_ticket_cat.create_text_channel(
            name=f"{ctx.author.name}-{issue_num}",
            reason="Making a ticket.",
            overwrites=overwrites,
        )
        await ticket_chnl.set_permissions(ctx.message.author, read_messages=True)
        for x in MOD_ROLES:
            role = nextcord.utils.get(ctx.guild.roles, name=x)
            if role is not None:
                await ticket_chnl.set_permissions(role, read_messages=True)

        await ticket_chnl.send(f"<@{ctx.author.id}> {CLAIMED_MESSAGE}")

    @ticket.command(aliases=["resolved"], brief="Marks your ticket as resolved")
    async def resolve(self, ctx, *args):
        if ctx.channel.category.name != ACTIVE_TICKETS_CAT_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in an active channel"
            )

        resolved_ticket_cat = await self.get_or_create_resolved_cat(ctx)
        await ctx.channel.edit(category=resolved_ticket_cat)

        await ctx.channel.send(RESOLVED_MESSAGE)

    @ticket.command(brief="Reopens a resolved ticket")
    async def reopen(self, ctx, *args):
        if ctx.channel.category.name != RESOLVED_TICKETS_CAT_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a resolved channel"
            )

        active_ticket_cat = await self.get_or_create_active_cat(ctx)
        await ctx.channel.edit(category=active_ticket_cat)

        await ctx.channel.send(REOPENED_MESSAGE)

    @ticket.command(
        brief="Scraps a resolved ticket, logs the messages and deletes the channel"
    )
    @commands.has_any_role(*MOD_ROLES)
    async def scrap(self, ctx, *args):
        if ctx.channel.category.name != RESOLVED_TICKETS_CAT_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a resolved channel"
            )

        tickets_log = await self.get_or_create_tickets_log(ctx)
        msg_list = await ctx.channel.history(limit=500, oldest_first=True).flatten()
        for msg in msg_list:
            emb = await self.get_tickets_log_embed(msg)
            await tickets_log.send(embed=emb)

        await ctx.channel.delete()

    async def get_tickets_log_embed(self, message):
        embed = nextcord.Embed(colour=DARK_BLUE)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        content_msg = "[Empty message]"
        if len(message.content) > 0:
            content_msg = message.content
            if len(content_msg) > 1800:
                content_msg = content_msg[0:1800]
                content_msg += " [Message too long to be logged]"
        embed.set_thumbnail(url=message.author.avatar.url)
        embed.title = message.author.name
        embed.description = content_msg
        embed.add_field(name="Channel", value=message.channel.name)
        embed.add_field(name="Date", value=message.created_at)
        return embed

    async def create_claimable_channel(self, cat):
        chnl = await cat.create_text_channel(
            name=CLAIMABLE_CHANNEL_NAME, reason="Making a claimable channel."
        )
        muted_role = nextcord.utils.get(cat.guild.roles, name="Muted")
        if muted_role:
            await chnl.set_permissions(muted_role, send_messages=True)
        await chnl.send(CLAIMABLE_CHANNEL_MESSAGE)

    async def get_or_create_tickets_log(self, ctx):
        resolved_cat = await self.get_or_create_resolved_cat(ctx)
        tickets_log = nextcord.utils.get(
            resolved_cat.channels, name=TICKETS_LOG_CHANNEL_NAME
        )
        if tickets_log is None:
            overwrites = {
                ctx.guild.default_role: nextcord.PermissionOverwrite(
                    read_messages=False
                )
            }

            tickets_log = await resolved_cat.create_text_channel(
                name=TICKETS_LOG_CHANNEL_NAME,
                reason="Making a channel for ticket logs.",
                overwrites=overwrites,
            )
            for x in MOD_ROLES:
                role = nextcord.utils.get(ctx.guild.roles, name=x)
                if role is not None:
                    await tickets_log.set_permissions(role, read_messages=True)
        return tickets_log

    async def get_or_create_claimable_cat(self, ctx):
        claimable_ticket_cat = nextcord.utils.get(
            ctx.guild.categories, name=CLAIMABLE_TICKETS_CAT_NAME
        )
        if claimable_ticket_cat is None:
            claimable_ticket_cat = await ctx.guild.create_category(
                name=CLAIMABLE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return claimable_ticket_cat

    async def get_or_create_active_cat(self, ctx):
        active_ticket_cat = nextcord.utils.get(
            ctx.guild.categories, name=ACTIVE_TICKETS_CAT_NAME
        )
        if active_ticket_cat is None:
            active_ticket_cat = await ctx.guild.create_category(
                name=ACTIVE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return active_ticket_cat

    async def get_or_create_resolved_cat(self, ctx):
        resolved_ticket_cat = nextcord.utils.get(
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
            try:
                if int(lst[-1]) > num:
                    num = int(lst[-1])
            except Exception:
                print(f"debug: {lst} has no number")

        for x in resolved_ticket_cat.channels:
            lst = x.name.split("-")
            try:
                if int(lst[-1]) > num:
                    num = int(lst[-1])
            except Exception:
                print(f"debug: {lst} has no number")

        return num


def setup(bot):
    bot.add_cog(Tickets(bot))
