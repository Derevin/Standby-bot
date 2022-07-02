from nextcord.ext import commands
import nextcord
from nextcord import Interaction, SlashOption
from cogs.error_handler import unhandled_error_embed
from settings import *
from inspect import Parameter
from utils.util_functions import *

CLAIMABLE_TICKETS_CAT_NAME = "Talk to mods"
CLAIMABLE_CHANNEL_NAME = "ticket-channel"
ACTIVE_TICKETS_CAT_NAME = "Active tickets"
RESOLVED_TICKETS_CAT_NAME = "Resolved tickets"
TICKETS_LOG_CHANNEL_NAME = "tickets-log"
CLAIMABLE_CHANNEL_MESSAGE = (
    "If you have an issue and want to talk to the mod team, this is the place.\n"
    "Use the `/ticket` command and choose the `Create` option to open a ticket.\n"
    "This will open a private channel visible only to you and the mod team."
)
CLAIMED_MESSAGE = (
    "You have successfully opened a ticket - please let us know what you want to discuss.\n"
    "You can make sure you're talking only to the mod team by looking "
    "at the channel's current member list (right side of discord).\n"
    "Once this issue has been resolved, use the `/ticket` command and choose the `Resolve` option."
)

RESOLVED_MESSAGE = (
    "This ticket has been marked as resolved."
    " If this was a mistake or you have additional questions, use the `/ticket` command and choose the `Reopen` option\n"
    "For other issues, please create a new ticket in XXX.\n"
    "Moderators can use the `/scrap` command to scrap this ticket. (Scrapping takes a while to complete)"
)

REOPENED_MESSAGE = "This ticket has been reopened. Once it is resolved, use the`/ticket` command and choose the `Resolve` option again."


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

    async def create(self, interaction):

        claimable_channel = get_channel(interaction.guild, CLAIMABLE_CHANNEL_NAME)
        if interaction.channel != claimable_channel:

            await interaction.send(
                f"This command can only be used in {claimable_channel.mention}.",
                ephemeral=True,
            )
            return

        issue_num = await self.get_highest_num(interaction) + 1

        active_ticket_cat = await self.get_or_create_active_cat(interaction)
        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(
                read_messages=False
            )
        }

        ticket_chnl = await active_ticket_cat.create_text_channel(
            name=f"{interaction.user.name}-{issue_num}",
            reason="Making a ticket.",
            overwrites=overwrites,
        )
        await ticket_chnl.set_permissions(interaction.user, read_messages=True)
        for x in MOD_ROLES:
            role = nextcord.utils.get(interaction.guild.roles, name=x)
            if role is not None:
                await ticket_chnl.set_permissions(role, read_messages=True)

        await ticket_chnl.send(f"<@{interaction.user.id}> {CLAIMED_MESSAGE}")
        await interaction.send(
            f"You can now head over to {ticket_chnl.mention}.", ephemeral=True
        )

    async def resolve(self, interaction):
        if interaction.channel.category.name != ACTIVE_TICKETS_CAT_NAME:
            await interaction.send(
                "This command can only be used in an active ticket channel",
                ephemeral=True,
            )
            return

        resolved_ticket_cat = await self.get_or_create_resolved_cat(interaction)
        await interaction.channel.edit(category=resolved_ticket_cat)

        claimable_channel = get_channel(interaction.guild, CLAIMABLE_CHANNEL_NAME)
        await interaction.send(
            RESOLVED_MESSAGE.replace("XXX", claimable_channel.mention)
        )

    async def reopen(self, interaction):
        if interaction.channel.category.name != RESOLVED_TICKETS_CAT_NAME:
            await interaction.send(
                "This command can only be used in a resolved channel",
                ephemeral=True,
            )
            return

        active_ticket_cat = await self.get_or_create_active_cat(interaction)
        await interaction.channel.edit(category=active_ticket_cat)

        await interaction.send(REOPENED_MESSAGE)

    @nextcord.slash_command(
        description="Create or manage tickets to discuss matters privately with the mod team",
    )
    async def ticket(
        self,
        interaction,
        action=SlashOption(
            description="Choose the action you want to take",
            choices=["Create", "Resolve", "Reopen"],
        ),
    ):
        args_dict = {
            "Create": self.create,
            "Resolve": self.resolve,
            "Reopen": self.reopen,
        }
        command = args_dict[action]
        await command(interaction)

    @nextcord.slash_command(
        description="Initiates ticket system - creates categories, channels etc",
        default_member_permissions=MODS_AND_GUIDES,
    )
    #
    async def initiate_ticket_system(self, interaction):
        claimable_ticket_cat = await self.get_or_create_claimable_cat(interaction)
        if not claimable_ticket_cat.channels:
            await self.create_claimable_channel(claimable_ticket_cat)
        await self.get_or_create_active_cat(interaction)
        await self.get_or_create_resolved_cat(interaction)
        await self.get_or_create_tickets_log(interaction)
        await interaction.send("Ticket system succesfully initiated", ephemeral=True)

    @nextcord.slash_command(
        description="Scraps a resolved ticket, logs the messages and deletes the channel",
        default_member_permissions=MODS_AND_GUIDES,
    )
    async def scrap(self, interaction):
        if interaction.channel.category.name != RESOLVED_TICKETS_CAT_NAME:
            await interaction.send(
                "This command can only be used in a resolved channel", ephemeral=True
            )
            return

        await interaction.send("Scrapping in progress", ephemeral=True)
        tickets_log = await self.get_or_create_tickets_log(interaction)
        msg_list = await interaction.channel.history(
            limit=500, oldest_first=True
        ).flatten()
        for msg in msg_list:
            emb = await self.get_tickets_log_embed(msg)
            await tickets_log.send(embed=emb)

        await interaction.channel.delete()

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
        if message.author.display_avatar:
            embed.set_thumbnail(url=message.author.display_avatar.url)
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

    async def get_or_create_tickets_log(self, interaction):
        resolved_cat = await self.get_or_create_resolved_cat(interaction)
        tickets_log = nextcord.utils.get(
            resolved_cat.channels, name=TICKETS_LOG_CHANNEL_NAME
        )
        if tickets_log is None:
            overwrites = {
                interaction.guild.default_role: nextcord.PermissionOverwrite(
                    read_messages=False
                )
            }

            tickets_log = await resolved_cat.create_text_channel(
                name=TICKETS_LOG_CHANNEL_NAME,
                reason="Making a channel for ticket logs.",
                overwrites=overwrites,
            )
            for x in MOD_ROLES:
                role = nextcord.utils.get(interaction.guild.roles, name=x)
                if role is not None:
                    await tickets_log.set_permissions(role, read_messages=True)
        return tickets_log

    async def get_or_create_claimable_cat(self, interaction):
        claimable_ticket_cat = nextcord.utils.get(
            interaction.guild.categories, name=CLAIMABLE_TICKETS_CAT_NAME
        )
        if claimable_ticket_cat is None:
            claimable_ticket_cat = await interaction.guild.create_category(
                name=CLAIMABLE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return claimable_ticket_cat

    async def get_or_create_active_cat(self, interaction):
        active_ticket_cat = nextcord.utils.get(
            interaction.guild.categories, name=ACTIVE_TICKETS_CAT_NAME
        )
        if active_ticket_cat is None:
            active_ticket_cat = await interaction.guild.create_category(
                name=ACTIVE_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return active_ticket_cat

    async def get_or_create_resolved_cat(self, interaction):
        resolved_ticket_cat = nextcord.utils.get(
            interaction.guild.categories, name=RESOLVED_TICKETS_CAT_NAME
        )
        if resolved_ticket_cat is None:
            resolved_ticket_cat = await interaction.guild.create_category(
                name=RESOLVED_TICKETS_CAT_NAME,
                reason="Making a category for claimable tickets.",
            )
        return resolved_ticket_cat

    async def get_highest_num(self, interaction):
        active_ticket_cat = await self.get_or_create_active_cat(interaction)
        resolved_ticket_cat = await self.get_or_create_resolved_cat(interaction)

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
