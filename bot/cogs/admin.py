from discord.ext import commands
import discord
import asyncio
import random
import re
import datetime
from settings import *


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Displays basic server stats")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def status(self, ctx, *args):
        guild = ctx.guild

        n_voice = len(guild.voice_channels)
        n_text = len(guild.text_channels)
        embed = discord.Embed()
        embed.add_field(name="Server Name", value=guild.name, inline=False)
        embed.add_field(name="Server ID", value=guild.id)
        embed.add_field(name="# Voice channels", value=n_voice, inline=False)
        embed.add_field(name="# Text channels", value=n_text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["pong"], brief="Pong!")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def ping(self, ctx):
        await ctx.send("Ponguu!")

    @commands.command(brief="Sends a message through the bot to a chosen channel")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def say(self, ctx, channel_name, *message):
        await ctx.message.delete()
        channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel:
            if message:
                msg = " ".join(message)
                await channel.send(msg)
            else:
                raise commands.errors.BadArgument("Please enter a message")
        else:
            raise commands.errors.BadArgument(
                "Please enter a valid channel, no leading #"
            )

    @commands.command(brief="Leaves several ghost pings for a user")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def punish(self, ctx, user_mention):
        await ctx.message.delete()
        guild = ctx.guild
        ch_list = [
            "general",
            "legs-and-cows-and-whatever",
            "off-topic",
            "shit-post",
            "animu",
            "bot-spam",
        ]

        for ch in ch_list:
            channel = discord.utils.get(guild.text_channels, name=ch)
            if channel:
                ping = await channel.send(user_mention)
                await ping.delete()
                await asyncio.sleep(2)

        await asyncio.sleep(45)

        for ch in ch_list:
            channel = discord.utils.get(guild.text_channels, name=ch)
            if channel:
                ping = await channel.send(user_mention)
                await ping.delete()
                await asyncio.sleep(2)

    @commands.command(brief="Adds a reaction to a post")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def react(self, ctx, channel_name, msg_id, emoji):
        channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel:
            try:
                msg = await channel.fetch_message(msg_id)
            except Exception:
                raise commands.errors.BadArgument("No message found with that ID")

        else:
            raise commands.errors.BadArgument(
                "Please enter a valid channel, no leading #"
            )

        await msg.add_reaction(emoji)
        await ctx.message.delete()

    @commands.command(
        aliases=["clean"],
        brief="Clears the last X messages sent in the channel (max 20)",
    )
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def clear(self, ctx, amount):
        await ctx.message.delete()
        deleted = 0
        async for msg in ctx.channel.history(limit=20):
            await msg.delete()
            deleted += 1
            if deleted == int(amount):
                break
        reply = await ctx.send(
            f":white_check_mark: Deleted the last {deleted} messages! :white_check_mark:"
        )
        await asyncio.sleep(3)
        await reply.delete()

    @commands.command(brief="Moves a post from one channel to another",)
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def move(self, ctx, msg_id, to_channel, from_channel=None):

        cmd = re.split(" ", ctx.message.content)[0][1:]

        await ctx.message.delete()

        if not from_channel:
            from_channel = ctx.channel
        else:
            from_channel = discord.utils.get(ctx.guild.text_channels, name=from_channel)

        to_channel = discord.utils.get(ctx.guild.text_channels, name=to_channel)

        if not (to_channel and from_channel):
            raise commands.errors.BadArgument(
                "Please enter valid channel names, no leading #"
            )
        try:
            msg = await from_channel.fetch_message(int(msg_id))
        except Exception:
            raise commands.errors.BadArgument("No message found with that ID")

        embed = message_embed(msg, cmd, ctx.author)

        await to_channel.send(embed=embed)
        if cmd == "move":
            await msg.delete()

    @commands.command(brief="Copies a post from one channel to another")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def copy(self, ctx, msg_id, to_channel, from_channel=None):
        await ctx.invoke(
            self.bot.get_command("move"),
            msg_id=msg_id,
            to_channel=to_channel,
            from_channel=from_channel,
        )

    @commands.command(brief="Reposts the last 'user left' message to a channel")
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def obit(self, ctx, channel_name, *msg_id):
        channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
        if channel:
            if msg_id:
                msg_id = int(msg_id[0])
                try:
                    msg = await ctx.channel.fetch_message(msg_id)
                    if isLeaveMessage(msg):
                        await channel.send(embed=msg.embeds[0])
                except Exception:
                    raise commands.errors.BadArgument("No message found with that ID")

            else:
                async for msg in ctx.channel.history(limit=6):
                    if isLeaveMessage(msg):
                        await channel.send(embed=msg.embeds[0])
                        break
        await ctx.message.delete()


def message_embed(msg, cmd, trigger_author) -> discord.Embed:

    embed_titles = {
        "copy": "Copied message",
        "move": "Moved message",
        "link": "Message preview",
    }

    trigger_field_titles = {
        "move": "Moved by",
        "copy": "Copied by",
        "link": "Linked by",
    }

    embed = discord.Embed(color=PALE_BLUE)
    embed.title = embed_titles[cmd]
    embed.set_thumbnail(url=msg.author.avatar_url)
    embed.description = msg.content
    embed.add_field(name="Channel", value=msg.channel.mention)
    timestamp = msg.created_at + datetime.timedelta(hours=2)
    if (datetime.datetime.now() - timestamp).days > 11 * 30:
        timestamp = timestamp.strftime("%b %d, %Y")
    else:
        timestamp = timestamp.strftime("%b %d, %H:%M")
    embed.add_field(name="Sent at", value=timestamp)
    embed.add_field(name=EMPTY, value=EMPTY)
    embed.add_field(name="Original poster", value=msg.author.mention)

    embed.add_field(name=trigger_field_titles[cmd], value=trigger_author.mention)

    if cmd == "copy" or cmd == "link":
        embed.add_field(name="Link to message", value=f"[Click here]({msg.jump_url})")

    if msg.attachments:
        embed.set_image(url=msg.attachments[0].url)
    else:
        link = re.search(r"(https:.*\.(jpe?g|png|gif))", msg.content)
        if link:
            embed.set_image(url=link.group(1))

    return embed


def isLeaveMessage(message):
    return (
        message.author.id == BOT_ID
        and message.embeds
        and message.embeds[0].title == "The void grows smaller..."
    )


def setup(bot):
    bot.add_cog(Admin(bot))
