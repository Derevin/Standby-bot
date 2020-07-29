from discord.ext import commands
import discord

class Admin(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def status(self, ctx, *args):
    guild = ctx.guild

    n_voice = len(guild.voice_channels)
    n_text = len(guild.text_channels)
    embed = discord.Embed()
    embed.add_field(name="Server Name",value=guild.name, inline=False)
    embed.add_field(name="# Voice channels",value=n_voice, inline=False)
    embed.add_field(name="# Text channels",value=n_text, inline=False)
    await ctx.send(embed=embed)

  @commands.command()
  async def ping(self, ctx):
    await ctx.send("Ponguu!")    

def setup(bot):
  bot.add_cog(Admin(bot))