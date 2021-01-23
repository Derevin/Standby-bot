from discord.ext import commands
import discord
import random
from utils.util_functions import *
from settings import *
from fuzzywuzzy import process


TOUCAN_PRAISE = """
░░░░░░░░▄▄▄▀▀▀▄▄███▄░░░░░░░░░░░░░░
░░░░░▄▀▀░░░░░░░▐░▀██▌░░░░░░░░░░░░░
░░░▄▀░░░░▄▄███░▌▀▀░▀█░░░░░░░░░░░░░
░░▄█░░▄▀▀▒▒▒▒▒▄▐░░░░█▌░░░░░░░░░░░░
░▐█▀▄▀▄▄▄▄▀▀▀▀▌░░░░░▐█▄░░░░░░░░░░░
░▌▄▄▀▀░░░░░░░░▌░░░░▄███████▄░░░░░░
░░░░░░░░░░░░░▐░░░░▐███████████▄░░░
░░░░░le░░░░░░░▐░░░░▐█████████████▄
░░░░toucan░░░░░░▀▄░░░▐█████████████▄
░░░░░░has░░░░░░░░▀▄▄███████████████
░░░░░arrived░░░░░░░░░░░░█▀██████░░
"""


memes = {
    "invest": "https://cdn.discordapp.com/attachments/744224801429782679/799296186019741696/Invest_Button_Banner.png",
    "chad yes": "https://cdn.discordapp.com/attachments/744224801429782679/799296476835610674/cover5.png",
    "pointing spiderman": "https://cdn.discordapp.com/attachments/744224801429782679/799298056373534800/C-658VsXoAo3ovC.png",
    "always has been": "https://cdn.discordapp.com/attachments/744224801429782679/802392943620915220/Always-Has-Been.png",
}


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Praises toucan")
    async def praise(self, ctx):
        await ctx.channel.send(TOUCAN_PRAISE)

    @commands.command(brief="Praise screenshot")
    async def praisepic(self, ctx):
        await ctx.channel.send(
            "https://cdn.discordapp.com/attachments/743071403447943269/756976939591270431/unknown.png"
        )

    @commands.command(brief="Posts a random 'horny' warning")
    async def horny(self, ctx):
        links = [
            "https://cdn.discordapp.com/attachments/267554564838785024/667115013412225054/image0.jpg",
            "https://i.kym-cdn.com/entries/icons/original/000/033/758/Screen_Shot_2020-04-28_at_12.21.48_PM.png",
            "https://cdn.discordapp.com/attachments/267554564838785024/701271178790305852/horny.jpg",
            "https://cdn.discordapp.com/attachments/267554564838785024/708425147064909944/x3x53kej4jr31.png",
            "https://cdn.discordapp.com/attachments/258941607238172673/717436181901475990/anti_horny.jpg",
            "https://cdn.discordapp.com/attachments/620408411393228809/724613520318267422/ubil7fxr99551.png",
        ]
        if ctx.author.id == JORM_ID:
            await ctx.channel.send(links[5])
        else:
            await ctx.channel.send(random.choice(links))

    @commands.command(brief="Posts an 'anime' warning")
    async def anime(self, ctx):
        await ctx.channel.send(
            "https://cdn.discordapp.com/attachments/744224801429782679/758417628544106546/4fmrlk.png"
        )

    @commands.command(brief="Posts a 'cringe' warning")
    async def cringe(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/441286267548729345/709160523907989524/EVACI9dUcAQp2Mb.png"
        )

    @commands.command(brief="Gives a user a hug")
    async def hug(self, ctx, *, user):

        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        else:
            user = get_user(ctx.guild, user)

        if user:
            if user == ctx.author:
                await ctx.send(
                    "https://cdn.discordapp.com/attachments/744224801429782679/757549246533599292/selfhug.png"
                )
            else:
                await ctx.channel.send(
                    f"{user.mention}, {ctx.author.mention} sent you a hug!"
                )
                hug = get_emoji(ctx.guild, "BlobReachAndHug")
                if hug:
                    await ctx.channel.send(hug)

    @commands.command(brief="Pay your respects", aliases=["F"])
    async def f(self, ctx, *target):
        embed = discord.Embed()
        embed.description = (
            f"**{ctx.author.name}** has paid their respects"
            + (f" to **{' '.join(target)}**" if target else "")
            + "."
        )
        rip = await ctx.channel.send(embed=embed)
        await rip.add_reaction("🇫")

    @commands.command(brief="Posts a meme")
    async def meme(self, ctx, *, query):
        best_match = process.extractOne(query, list(memes.keys()), score_cutoff=67)
        if best_match:
            await ctx.send(memes[best_match[0]])


def setup(bot):
    bot.add_cog(Fun(bot))
