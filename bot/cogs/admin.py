from discord.ext import commands
import discord
import asyncio
import random


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
    async def repeat(self, ctx, *args):
        txt = ""
        for s in args:
            txt += " "
            txt += s
        await ctx.send(txt)

    @commands.command()
    async def repeatMessage(self, ctx):
        await ctx.send(ctx.message.content)

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def say(self, ctx, *args):
        guild = ctx.guild
        channel = discord.utils.get(guild.text_channels, name=args[0])
        msg = " ".join(args[1:])
        if channel is not None:
            await channel.send(msg)

    @commands.command()
    @commands.has_any_role("Moderator", "Guides of the Void")
    async def punish(self, ctx, arg):
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
            ping = await channel.send(arg)
            await ping.delete()
            await asyncio.sleep(2)

        await asyncio.sleep(45)

        for ch in ch_list:
            channel = discord.utils.get(guild.text_channels, name=ch)
            ping = await channel.send(arg)
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


def setup(bot):
    bot.add_cog(Admin(bot))
