import aiohttp
from discord.ext import commands
import discord
import random


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Random cat")
    async def cat(self, ctx):
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    "https://api.thecatapi.com/v1/images/search?size=full"
                ) as r:
                    data = await r.json()

                    embed = discord.Embed(title="Meow")
                    embed.set_image(url=data[0]["url"])
                    embed.set_footer(text="https://thecatapi.com")

                    await ctx.send(embed=embed)

    @commands.command(brief="Random dog")
    async def dog(self, ctx):
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://dog.ceo/api/breeds/image/random") as r:
                    data = await r.json()

                    embed = discord.Embed(title="Woof")
                    embed.set_image(url=data["message"])
                    embed.set_footer(text="https://dog.ceo")

                    await ctx.send(embed=embed)

    @commands.command(brief="Random fox")
    async def fox(self, ctx):
        async with ctx.channel.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://randomfox.ca/floof/") as r:
                    data = await r.json()

                    embed = discord.Embed(title="What does the fox say")
                    embed.set_image(url=data["image"])
                    embed.set_footer(text="https://randomfox.ca")

                    await ctx.send(embed=embed)

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
    async def cringe(self, ctx):
        await ctx.message.delete()
        await ctx.send(
            "https://cdn.discordapp.com/attachments/441286267548729345/709160523907989524/EVACI9dUcAQp2Mb.png"
        )


def setup(bot):
    bot.add_cog(Images(bot))
