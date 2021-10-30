from discord.ext import commands
import discord
import asyncio
import random
import re
import datetime
from PIL import Image, ImageFilter
import requests
import io
from settings import *
from utils.util_functions import *
import json


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Displays basic server stats")
    @commands.has_any_role(*MOD_ROLES)
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
    @commands.has_any_role(*MOD_ROLES)
    async def ping(self, ctx):
        await ctx.send("Ponguu!")

    @commands.command(brief="Sends a message through the bot to a chosen channel")
    @commands.has_any_role(*MOD_ROLES)
    async def say(self, ctx, channel_name, *, message):
        await ctx.message.delete()
        channel = get_channel(ctx.guild, channel_name)
        if channel:
            await channel.send(message)
        else:
            raise commands.errors.BadArgument(
                "Please enter a valid channel name or mention"
            )

    @commands.command(brief="Edits a bot message")
    @commands.has_any_role(*MOD_ROLES)
    async def edit(self, ctx, channel_name, id, *, text):
        await ctx.message.delete()
        channel = get_channel(ctx.guild, channel_name)
        try:
            message = await channel.fetch_message(int(id))
        except Exception:
            raise commands.errors.BadArgument("No message found with that ID")
        if message.author.bot:
            await message.edit(content=text)

    @commands.command(brief="Responds to a message")
    @commands.has_any_role(*MOD_ROLES)
    async def reply(self, ctx, channel_name, reply_msg_id, *, message):
        await ctx.message.delete()
        channel = get_channel(ctx.guild, channel_name)
        try:
            reply_msg = await channel.fetch_message(int(reply_msg_id))
        except Exception:
            raise commands.errors.BadArgument("No message found with that ID")
        await channel.send(message, reference=reply_msg)

    @commands.command(brief="Leaves several ghost pings for a user")
    @commands.has_any_role(*MOD_ROLES)
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
            channel = get_channel(guild, ch)
            if channel:
                ping = await channel.send(user_mention)
                await ping.delete()
                await asyncio.sleep(2)

        await asyncio.sleep(45)

        for ch in ch_list:
            channel = get_channel(guild, ch)
            if channel:
                ping = await channel.send(user_mention)
                await ping.delete()
                await asyncio.sleep(2)

    @commands.command(brief="Adds a reaction to a post")
    @commands.has_any_role(*MOD_ROLES)
    async def react(self, ctx, channel_name, msg_id, *emojis):
        channel = get_channel(ctx.guild, channel_name)
        if channel:
            try:
                msg = await channel.fetch_message(msg_id)
            except Exception:
                raise commands.errors.BadArgument("No message found with that ID")

        else:
            raise commands.errors.BadArgument(
                "Please enter a valid channel name or mention"
            )

        for emoji in emojis:
            await msg.add_reaction(emoji)
        await ctx.message.delete()

    @commands.command(
        aliases=["clean"],
        brief="Clears the last X messages sent in the channel (max 20)",
    )
    @commands.has_any_role(*MOD_ROLES)
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

    @commands.command(
        brief="Moves a post from one channel to another",
        aliases=["copy"],
        help="Use as a reply to the target message",
    )
    @commands.has_any_role(*MOD_ROLES)
    async def move(self, ctx, to_channel):

        cmd = re.split(" ", ctx.message.content)[0][1:]

        # await ctx.message.delete()

        if not ctx.message.reference:
            raise commands.errors.UserInputError(
                "Use this command as a reply to the target message"
            )

        if not to_channel:
            raise commands.errors.BadArgument(
                "Please enter a valid channel name or mention"
            )

        to_channel = get_channel(ctx.guild, to_channel)

        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)

        embed = message_embed(msg, cmd, ctx.author)

        await to_channel.send(embed=embed)

        await ctx.message.delete()

        if cmd == "move":
            await msg.delete()

    @commands.command(brief="Reposts the last 'user left' message to a channel")
    @commands.has_any_role(*MOD_ROLES)
    async def obit(self, ctx, channel_name):
        channel = get_channel(ctx.guild, channel_name)
        if channel:
            if ctx.message.reference:
                msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                if isLeaveMessage(msg):
                    await channel.send(embed=msg.embeds[0])

            else:
                async for msg in ctx.channel.history(limit=6):
                    if isLeaveMessage(msg):
                        await channel.send(embed=msg.embeds[0])
                        break
        await ctx.message.delete()

    @commands.command(brief="Starts a vote")
    @commands.has_any_role(*MOD_ROLES)
    async def vote(self, ctx, *, topic):
        await ctx.message.delete()

        if ctx.channel.name not in ["mod-chat", "mod-votes"]:
            raise commands.errors.CommandError(
                "You can only run this command in a mod channel."
            )

        embed = discord.Embed(color=PALE_YELLOW)
        embed.title = "A vote has been requested"
        embed.add_field(name="Started by", value=ctx.author.mention)

        await ctx.send("@here")

        if re.search(r"\d\. ", topic):
            topic = re.sub(r"(?<!\n)(\d)\. ", r"\n\1\. ", topic)
            embed.description = topic
            options = re.findall(r"(?<=\n)\d", topic)
            vote_msg = await ctx.send(embed=embed)
            for num in options:
                await vote_msg.add_reaction(int_to_emoji(int(num)))
        else:
            embed.description = topic
            vote_msg = await ctx.send(embed=embed)
            await vote_msg.add_reaction("✅")
            await vote_msg.add_reaction("❌")

    @commands.command(brief="Puts people in horny jail")
    @commands.has_any_role(*MOD_ROLES)
    async def hornyjail(self, ctx, offenders):
        if ctx.message.mentions:
            horny = get_role(ctx.guild, "horny")
            muted = get_role(ctx.guild, "Muted")
            jail = get_channel(ctx.guild, "horny-jail")
            if horny and muted:
                for offender in ctx.message.mentions:
                    await offender.add_roles(horny)
                    await offender.add_roles(muted)
                    if jail:
                        await jail.send(
                            f"Welcome to horny jail, {offender.mention}. Do not enjoy your stay."
                        )
                        await jail.send(
                            "https://cdn.discordapp.com/attachments/744224801429782679/819163418258702336/46zenaxz1td61.png"
                        )

    @commands.command(brief="Releases people from horny jail")
    @commands.has_any_role(*MOD_ROLES)
    async def hornyrelease(self, ctx, prisoners):
        if ctx.message.mentions:
            horny = get_role(ctx.guild, "horny")
            muted = get_role(ctx.guild, "Muted")
            if horny and muted:
                for prisoner in ctx.message.mentions:
                    await prisoner.remove_roles(horny)
                    await prisoner.remove_roles(muted)

    @commands.command(brief="Voidifies the mentioned user's avatar.")
    @commands.has_any_role(*MOD_ROLES)
    async def voidify(self, ctx, target):

        if ctx.author.id != JORM_ID:
            await ctx.send("Jorm alone controls the void. Access denied.")
            return

        target = ctx.message.mentions[0]
        avatar_url = target.avatar_url
        avatar = Image.open(requests.get(avatar_url, stream=True).raw)
        avatar = avatar.convert("RGBA")
        border = Image.open(requests.get(GINNY_TRANSPARENT_URL, stream=True).raw)
        border = border.resize(avatar.size, Image.ANTIALIAS)
        avatar.paste(border, (0, 0), border)

        newImage = []
        border_white = Image.open(requests.get(GINNY_WHITE_URL, stream=True).raw)
        border_white = border_white.resize(avatar.size, Image.ANTIALIAS)
        white_data = border_white.getdata()
        avatar_data = avatar.getdata()
        for i in range(len(white_data)):
            if white_data[i] == (255, 255, 255, 255):
                newImage.append((0, 0, 0, 0))
            else:
                newImage.append(avatar_data[i])
        avatar.putdata(newImage)

        obj = io.BytesIO()
        avatar.save(obj, "png")
        obj.seek(0)

        await ctx.send(file=discord.File(obj, filename="pic.png"))

    @commands.command(brief="Print a database table")
    @commands.has_any_role(*MOD_ROLES)
    async def printDB(self, ctx, table="tmers"):

        try:
            gtable = await self.bot.pg_pool.fetch(f"SELECT * FROM {table}")
        except Exception:
            await ctx.send(f"Table `{table}` not found.")
        else:
            if gtable:
                for rec in gtable:
                    d = rec
                    text = ""
                    for key, value in d.items():
                        text += key + ": " + str(value) + "\n"
                    await ctx.send(text)
            else:
                await ctx.send(f"Table `{table}` is empty.")


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
