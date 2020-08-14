from discord.ext import commands
import discord
from settings import *
from inspect import Parameter


CLAIMABLE_TICKETS_CAT_NAME = "Talk to mods"
CLAIMABLE_CHANNEL_NAME = "claim-this-channel"
ACTIVE_TICKETS_CAT_NAME = "Active tickets"
RESOLVED_TICKETS_CAT_NAME = "Resolved tickets"
TICKETS_LOG_CHANNEL_NAME = "tickets-log"
CLAIMABLE_CHANNEL_MESSAGE = (
    "If you want to talk to the mod team, this is the place!\n"
    "Claim this channel by typing: ```+tclaim```"
    " and then this channel will be restricted for your and mod-team eyes only.\n"
    "Disclaimer: It is recommended to mute this channel's category,"
    " otherwise you will get an unread message notification "
    "everytime this channel gets recreated."
)
CLAIMED_MESSAGE = (
    "This channel has been claimed, please type what is it that you want to discuss.\n"
    "You can make sure you're talking only to the mod team by looking "
    "at current member list of the channel (right side of discord).\n"
    "Once this issue has been resolved, type: ```+tresolve```"
)

RESOLVED_MESSAGE = (
    "This issue has been marked as resolved."
    " If this was a mistake, type: ```+treopen``` otherwise open a new issue.\n"
    "This issue can be scrapped with ```+tscrap``` by moderators.\n"
    "Scrapping takes a while to complete."
)

REOPENED_MESSAGE = (
    "This issue has been reopened. Once the issue is resolved, type: ```+tresolved```"
)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if (
            str(message.channel.type) == "text"
            and str(message.channel.name) == CLAIMABLE_CHANNEL_NAME
        ):
            try:
                if (
                    str(message.content) != "+tclaim"
                    and str(message.content) != "+topen"
                ):
                    await message.delete()
            except Exception as e:
                if message.guild.id == GUILD_ID:
                    channel = discord.utils.get(
                        message.guild.text_channels, name=ERROR_CHANNEL_NAME
                    )
                    if channel is not None:
                        await channel.send(
                            embed=unhandled_error_embed(
                                message.content, message.channel, e
                            )
                        )

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def tinit(self, ctx, *args):
        open_ticket_cat = await self.get_or_create_open_cat(ctx)
        if not open_ticket_cat.channels:
            await self.create_claimable(open_ticket_cat)
        await self.get_or_create_active_cat(ctx)
        await self.get_or_create_resolved_cat(ctx)
        await self.get_or_create_tickets_log(ctx)

    @commands.command(aliases=["tclaim"])
    async def topen(self, ctx, *args):
        if ctx.channel.name != CLAIMABLE_CHANNEL_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a claimable channel"
            )

        issue_num = await self.get_highest_num(ctx) + 1

        active_ticket_cat = await self.get_or_create_active_cat(ctx)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        await ctx.channel.edit(
            name=f"{ctx.author.name}-{issue_num}",
            category=active_ticket_cat,
            overwrites=overwrites,
        )
        await ctx.channel.set_permissions(ctx.message.author, read_messages=True)
        for x in MOD_ROLES_NAMES:
            role = discord.utils.get(ctx.guild.roles, name=x)
            if role is not None:
                await ctx.channel.set_permissions(role, read_messages=True)

        await ctx.channel.send(CLAIMED_MESSAGE)

        open_ticket_cat = await self.get_or_create_open_cat(ctx)
        if not open_ticket_cat.channels:
            await self.create_claimable(open_ticket_cat)

    @commands.command()
    async def tresolve(self, ctx, *args):
        if ctx.channel.category.name != ACTIVE_TICKETS_CAT_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in an active channel"
            )

        resolved_ticket_cat = await self.get_or_create_resolved_cat(ctx)
        await ctx.channel.edit(category=resolved_ticket_cat)

        await ctx.channel.send(RESOLVED_MESSAGE)

    @commands.command()
    async def treopen(self, ctx, *args):
        if ctx.channel.category.name != RESOLVED_TICKETS_CAT_NAME:
            raise commands.errors.UserInputError(
                "This command can be used only in a resolved channel"
            )

        active_ticket_cat = await self.get_or_create_active_cat(ctx)
        await ctx.channel.edit(category=active_ticket_cat)

        await ctx.channel.send(REOPENED_MESSAGE)

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def tscrap(self, ctx, *args):
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
        embed = discord.Embed(colour=DARK_BLUE)
        if message.attachments:
            embed.set_image(url=message.attachments[0].url)
        content_msg = "[Empty message]"
        if len(message.content) > 0:
            content_msg = message.content
            if len(content_msg) > 1800:
                content_msg = content_msg[0:1800]
                content_msg += " [Message too long to be logged]"
        embed.set_thumbnail(url=message.author.avatar_url)
        embed.title = message.author.name
        embed.description = f"[{content_msg}]({message.jump_url})"
        embed.add_field(name="Channel", value=message.channel.name)
        embed.add_field(name="Date", value=message.created_at)
        return embed

    async def create_claimable(self, cat):
        chnl = await cat.create_text_channel(
            name=CLAIMABLE_CHANNEL_NAME, reason="Making a claimable channel."
        )
        await chnl.send(CLAIMABLE_CHANNEL_MESSAGE)

    async def get_or_create_tickets_log(self, ctx):
        resolved_cat = await self.get_or_create_resolved_cat(ctx)
        tickets_log = discord.utils.get(
            resolved_cat.channels, name=TICKETS_LOG_CHANNEL_NAME
        )
        if tickets_log is None:
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }

            tickets_log = await resolved_cat.create_text_channel(
                name=TICKETS_LOG_CHANNEL_NAME,
                reason="Making a channel for ticket logs.",
                overwrites=overwrites,
            )
            for x in MOD_ROLES_NAMES:
                role = discord.utils.get(ctx.guild.roles, name=x)
                if role is not None:
                    await tickets_log.set_permissions(role, read_messages=True)
        return tickets_log

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
            try:
                if int(lst[-1]) > num:
                    num = int(lst[-1])
            except Exception:
                print(lst, "has no number")

        for x in resolved_ticket_cat.channels:
            lst = x.name.split("-")
            try:
                if int(lst[-1]) > num:
                    num = int(lst[-1])
            except Exception:
                print(lst, "has no number")

        return num


def setup(bot):
    bot.add_cog(Tickets(bot))
