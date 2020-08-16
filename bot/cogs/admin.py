from discord.ext import commands
import discord
import asyncio
import random
import re


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
    async def horny(self, ctx):
        links = [
            "https://cdn.discordapp.com/attachments/267554564838785024/667115013412225054/image0.jpg",
            "https://i.kym-cdn.com/entries/icons/original/000/033/758/Screen_Shot_2020-04-28_at_12.21.48_PM.png",
            "https://cdn.discordapp.com/attachments/267554564838785024/701271178790305852/horny.jpg",
            "https://cdn.discordapp.com/attachments/267554564838785024/708425147064909944/x3x53kej4jr31.png",
            "https://cdn.discordapp.com/attachments/258941607238172673/717436181901475990/anti_horny.jpg",
            "https://cdn.discordapp.com/attachments/620408411393228809/724613520318267422/ubil7fxr99551.png",
        ]
        await ctx.message.delete()
        await ctx.channel.send(links[random.randint(0, len(links) - 1)])

    @commands.command()
    async def anime(self, ctx):
        await ctx.message.delete()
        await ctx.channel.send(
            "https://cdn.discordapp.com/attachments/355732809224028161/709500701134422137/anime_violation.png"
        )

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

    @commands.command()
    async def cringe(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/441286267548729345/709160523907989524/EVACI9dUcAQp2Mb.png"
        )

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


def setup(bot):
    bot.add_cog(Admin(bot))
