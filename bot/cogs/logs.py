from nextcord.ext import commands
import nextcord
from settings import *
from utils.util_functions import *
import datetime


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel.name == LOGS_CHANNEL_NAME:
            return
        embed, files = await deleted_embed(payload, channel)
        if embed:
            guild = channel.guild
            logs = nextcord.utils.get(guild.text_channels, name=LOGS_CHANNEL_NAME)
            if logs:
                main = await logs.send(embed=embed)
                for file in files:
                    await logs.send(file=file, reference=main)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):

        embed = await edited_embed(self.bot, payload)
        if embed:
            channel = self.bot.get_channel(payload.channel_id)
            guild = channel.guild
            logs = nextcord.utils.get(guild.text_channels, name=LOGS_CHANNEL_NAME)
            if logs:
                await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if before.channel == after.channel:
            return

        embed = await voice_embed(member, before.channel, after.channel)

        guild = member.guild
        logs = nextcord.utils.get(guild.text_channels, name=LOGS_CHANNEL_NAME)
        if logs:
            await logs.send(embed=embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.type != nextcord.InteractionType.application_command:
            return

        guild = interaction.guild
        logs = nextcord.utils.get(guild.text_channels, name=LOGS_CHANNEL_NAME)

        if logs:
            embed = await slash_embed(interaction)
            await logs.send(embed=embed)


async def deleted_embed(payload, channel):
    embed = nextcord.Embed(color=SOFT_RED)
    embed.title = "Message deleted"
    files = []
    if payload.cached_message is not None:
        message = payload.cached_message
        if message.author.bot or str(message.type) == "MessageType.pins_add":
            return None, None
        embed.description = message.content
        if len(embed.description) > 950:
            embed.description = embed.description[0:950]
            embed.description += "[Message had to be shortened]"

        if message.author.avatar:
            embed.set_thumbnail(url=message.author.avatar.url)
        embed.add_field(name="Author", value=message.author.mention)
        embed.add_field(name="Channel", value=message.channel.mention)
        if message.attachments:
            for attachment in message.attachments:
                file = await attachment.to_file()
                files.append(file)
            embed.add_field(name="Attachments", value="[See below]", inline=False)
    else:
        embed.description = "[Message not found in cache]"
        embed.add_field(name="Channel", value=channel.mention)
    embed.timestamp = nextcord.utils.utcnow()
    return embed, files


async def edited_embed(bot, payload):

    before = payload.cached_message
    after = payload.data
    if "content" in after:
        after_message = after["content"]
    else:
        return None
    attachment_url = None

    if before:

        author = before.author
        if author.bot:
            return None

        before_message = before.content
        if before_message == after_message:
            return None

        channel = before.channel
        jump_url = before.jump_url
        avatar_url = before.author.avatar.url if before.author.avatar else ""
        attachment_url = before.attachments[0].url if before.attachments else None

    else:

        before_message = "[Message not found in cache]"

        guild_id = after["guild_id"]
        author_id = after["author"]["id"]
        channel_id = after["channel_id"]
        message_id = after["id"]

        guild = await bot.fetch_guild(guild_id)
        author = await guild.fetch_member(author_id)
        if author.bot or not author:
            return None
        channel = await bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        jump_url = message.jump_url
        avatar_url = author.avatar.url if author.avatar else ""
        attachment_url = message.attachments[0].url if message.attachments else None

    embed = nextcord.Embed(color=LIGHT_BLUE)
    embed.title = "Message edited"
    if len(before_message) > 950:
        before_message = before_message[0:950]
        before_message += " [Message had to be shortened]"
    if len(after_message) > 600:
        after_message = after_message[0:950]
        after_message += " [Message had to be shortened]"
    if len(before_message) <= 0:
        before_message = "[empty]"
    if len(after_message) <= 0:
        after_message = "[empty]"
    embed.add_field(name="Before", value=before_message, inline=False)
    embed.add_field(name="After", value=after_message, inline=False)
    embed.add_field(name="Author", value=author.mention)
    embed.add_field(name="Channel", value=channel.mention)
    embed.add_field(name="Link to Message", value=f"[Click here]({jump_url})")
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)
    if attachment_url:
        embed.add_field(name="Attachment", value=f"[Click here]({attachment_url})")
    embed.timestamp = nextcord.utils.utcnow()

    return embed


async def voice_embed(member, before, after):
    embed = nextcord.Embed(color=PALE_BLUE)
    embed.title = "Voice channel update"

    if before and after:
        embed.description = (
            f"{member.mention} ({member.name}#{member.discriminator}) switched"
            f" voice channels from **#{before.name}** to **#{after.name}**"
        )
    elif before:
        embed.description = (
            f"{member.mention} ({member.name}#{member.discriminator}) left"
            f" voice channel **#{before.name}**"
        )
    else:
        embed.description = (
            f"{member.mention} ({member.name}#{member.discriminator}) joined"
            f" voice channel **#{after.name}**"
        )
    embed.timestamp = nextcord.utils.utcnow()
    return embed


async def slash_embed(interaction):

    embed = nextcord.Embed(color=VIE_PURPLE)
    embed.title = "Slash command triggered"
    embed.add_field(name="User", value=interaction.user.mention)
    embed.add_field(name="Channel", value=interaction.channel.mention)

    embed.add_field(
        name="Command",
        value="/" + str(interaction.application_command),
        inline=False,
    )

    if "options" in interaction.data:

        arg_data = interaction.data["options"]
        if "options" in arg_data[0]:
            arg_data = arg_data[0]["options"]

        for arg in arg_data:
            embed.add_field(name=arg["name"], value=arg["value"])

    avatar_url = interaction.user.avatar.url if interaction.user.avatar else ""

    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.timestamp = nextcord.utils.utcnow()

    return embed


def setup(bot):
    bot.add_cog(Logs(bot))
