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

    @commands.command()
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

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Ponguu!")

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command(aliases=["clean"])
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

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def move(self, ctx, msg_id, to_channel, from_channel=None):

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
        else:
            try:
                msg = await from_channel.fetch_message(int(msg_id))
            except Exception:
                raise commands.errors.BadArgument("No message found with that ID")

            embed = discord.Embed(color=PALE_BLUE)
            embed.title = "Moved message"
            embed.set_thumbnail(url=msg.author.avatar_url)
            embed.description = msg.content
            embed.add_field(
                name="Original poster", value=msg.author.mention, inline=True
            )
            embed.add_field(name="Channel", value=msg.channel.mention, inline=True)
            timestamp = msg.created_at + datetime.timedelta(hours=2)
            timestamp = timestamp.strftime("%b %d, %H:%M")
            embed.add_field(name="Sent at", value=timestamp, inline=True)
            if msg.attachments:
                embed.set_image(url=msg.attachments[0].url)
            elif re.search(r"^https:.*\.(jpe?g|png|gif)$", msg.content):
                embed.set_image(url=msg.content)
            await to_channel.send(embed=embed)
            await msg.delete()


def setup(bot):
    bot.add_cog(Admin(bot))
