import aiohttp
from discord.ext import commands
import discord

class Images(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command(brief="Random cat")
  async def cat(self, ctx):
    async with ctx.channel.typing():
      async with aiohttp.ClientSession() as cs:
        async with cs.get("https://api.thecatapi.com/v1/images/search?size=full") as r:
          data = await r.json()

          embed = discord.Embed(title = "Meow")
          embed.set_image(url=data[0]['url'])
          embed.set_footer(text = "https://thecatapi.com")

          await ctx.send(embed=embed)

  @commands.command(brief="Random dog")
  async def dog(self, ctx):
    async with ctx.channel.typing():
      async with aiohttp.ClientSession() as cs:
        async with cs.get("https://dog.ceo/api/breeds/image/random") as r:
          data = await r.json()

          embed = discord.Embed(title = "Woof")
          embed.set_image(url=data['message'])
          embed.set_footer(text = "https://dog.ceo")

          await ctx.send(embed=embed)

  @commands.command(brief="Random fox")
  async def fox(self, ctx):
    async with ctx.channel.typing():
      async with aiohttp.ClientSession() as cs:
        async with cs.get("https://randomfox.ca/floof/") as r:
          data = await r.json()

          embed = discord.Embed(title = "What does the fox say")
          embed.set_image(url=data['image'])
          embed.set_footer(text = "https://randomfox.ca")

          await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Images(bot))
