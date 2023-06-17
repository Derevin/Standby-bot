from nextcord import Embed, InteractionType, MessageType
from nextcord.ext.commands import Cog

from config.constants import *
from db_integration import db_functions as db
from utils import util_functions as uf


class Logs(Cog):
    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_raw_message_delete(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if channel.name == LOGS_CHANNEL_NAME:
            return
        embed, files = await deleted_embed(payload, channel)
        if embed:
            logs = uf.get_channel(channel.guild, LOGS_CHANNEL_NAME)
            if logs:
                main = await logs.send(embed=embed)
                for file in files:
                    await logs.send(file=file, reference=main)


    @Cog.listener()
    async def on_raw_message_edit(self, payload):
        embed = await edited_embed(self.bot, payload)
        if embed:
            channel = self.bot.get_channel(payload.channel_id)
            logs = uf.get_channel(channel.guild, LOGS_CHANNEL_NAME)
            if logs:
                await logs.send(embed=embed)


    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        embed = await voice_embed(member, before.channel, after.channel)

        logs = uf.get_channel(member.guild, LOGS_CHANNEL_NAME)
        if logs:
            await logs.send(embed=embed)


    @Cog.listener()
    async def on_interaction(self, interaction):
        logs = uf.get_channel(interaction.guild, LOGS_CHANNEL_NAME)

        if logs:
            if interaction.type == InteractionType.application_command:
                embed = await command_embed(interaction)
                await logs.send(embed=embed)
            elif interaction.type == InteractionType.component:
                embed = await component_embed(interaction)
                await logs.send(embed=embed)
            else:
                await db.log(self.bot, f"Unknown interaction in {interaction.channel.name} with {interaction.type=}")
                await logs.send(f"Unknown interaction in {interaction.channel.mention}.")
        else:
            await db.log(self.bot, "Log channel not found")


async def deleted_embed(payload, channel):
    embed = Embed(color=SOFT_RED)
    embed.title = "Message deleted"
    files = []
    if payload.cached_message is not None:
        message = payload.cached_message
        if message.author.bot or message.type == MessageType.pins_add:
            return None, None
        embed.description = message.content
        if len(embed.description) > 950:
            embed.description = embed.description[0:950]
            embed.description += "[Message had to be shortened]"

        if message.author.display_avatar:
            embed.set_thumbnail(url=message.author.display_avatar.url)
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
    embed.timestamp = uf.utcnow()
    return embed, files


async def edited_embed(bot, payload):
    before = payload.cached_message
    after = payload.data
    if "content" in after:
        after_message = after["content"]
    else:
        return None

    if before:
        author = before.author
        if author.bot:
            return None

        before_message = before.content
        if before_message == after_message:
            return None

        channel = before.channel
        jump_url = before.jump_url
        avatar_url = before.author.display_avatar.url

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
        avatar_url = author.display_avatar.url
        attachment_url = message.attachments[0].url if message.attachments else None

    embed = Embed(color=LIGHT_BLUE)
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
    embed.timestamp = uf.utcnow()

    return embed


async def voice_embed(member, before, after):
    embed = Embed(color=PALE_BLUE)
    embed.title = "Voice channel update"

    discriminator = f"#{member.discriminator}" if member.discriminator != "0" else ""

    if before and after:
        embed.description = (f"{member.mention} ({member.name}{discriminator}) switched"
                             f" voice channels from {before.mention} to {after.mention}")
    elif before:
        embed.description = (f"{member.mention} ({member.name}{discriminator}) left"
                             f" voice channel {before.mention}")
    else:
        embed.description = (f"{member.mention} ({member.name}{discriminator}) joined"
                             f" voice channel {after.mention}")
    embed.timestamp = uf.utcnow()
    return embed


async def command_embed(interaction):
    cmd_name = interaction.application_command.name
    cmd_type = str(interaction.application_command.type).split(".")[-1]
    if cmd_type == "chat_input":
        cmd_type = "Slash command"
    elif cmd_type == "sub_command":
        cmd_type = "Slash subcommand"
    elif cmd_type == "user_command":
        cmd_type = "User command"
    else:
        cmd_type = "Message command"

    cmd_prefix = "/" if "Slash" in cmd_type else "Apps > "

    embed = Embed(color=VIE_PURPLE)
    embed.title = f"{cmd_type} triggered"

    try:
        parent_name = interaction.application_command.parent_cmd.name + " "
    except AttributeError:
        parent_name = ""

    embed.add_field(name="Command", value=cmd_prefix + parent_name + cmd_name, inline=False)
    embed.add_field(name="Triggered by", value=interaction.user.mention)
    embed.add_field(name="In channel", value=interaction.channel.mention)

    if cmd_type == "User":
        embed.add_field(name="Target user", value=uf.id_to_mention(interaction.data["target_id"]))

    elif cmd_type == "Message":
        message_id = interaction.data["target_id"]
        message = await interaction.channel.fetch_message(message_id)

        embed.add_field(name="Target messsage", value=f"[Click here]({message.jump_url})")

    elif "options" in interaction.data:  # Slash
        embed.add_field(name=EMPTY, value=EMPTY)

        arg_data = interaction.data["options"]
        if "options" in arg_data[0]:
            arg_data = arg_data[0]["options"]

        for arg in arg_data:
            if arg["type"] == 6:
                formatted_value = uf.id_to_mention(arg["value"], "user")
            elif arg["type"] == 7:
                formatted_value = uf.id_to_mention(arg["value"], "channel")
            elif arg["type"] == 8:
                formatted_value = uf.id_to_mention(arg["value"], "role")
            else:
                formatted_value = arg["value"]

            embed.add_field(name=arg["name"], value=formatted_value)

    avatar_url = interaction.user.display_avatar.url
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    embed.timestamp = uf.utcnow()

    return embed


async def component_embed(interaction):
    embed = Embed(color=VIE_PURPLE)
    avatar_url = interaction.user.display_avatar.url
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)
    data = interaction.data
    if data["component_type"] == 2:  # Button
        embed.title = f"Button pressed"
        labels = [child.label for row in interaction.message.components for child in row.children if
                  child.custom_id == data["custom_id"]]
        embed.add_field(name="Button", value=labels[0] if len(labels) == 1 else "Unknown")
        embed.add_field(name="Pressed by", value=interaction.user.mention)
        embed.add_field(name="In channel", value=interaction.channel.mention)
    elif data["component_type"] == 3:  # Select
        embed.title = "Dropdown menu used"
        embed.add_field(name="Used by", value=interaction.user.mention)
        embed.add_field(name="In channel", value=interaction.channel.mention)
        name = "Value" + ("s" if len(data["values"]) > 1 else "")
        value = ", ".join(data["values"])
        if not value:
            value = "[Menu cleared]"
        embed.add_field(name=name, value=value)
    else:
        embed.title = f"Unknown component type {data['component_type']}"
        embed.add_field(name="Used by", value=interaction.user.mention)
        embed.add_field(name="In channel", value=interaction.channel.mention)
    embed.add_field(name="Link to message", value=f"[Click here]({interaction.message.jump_url})", inline=False)

    return embed


def setup(bot):
    bot.add_cog(Logs(bot))
