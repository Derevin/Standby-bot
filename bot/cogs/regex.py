from discord.ext import commands
import discord

class Regex(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, ctx, message)
    if "marco" in message.content.lower():
      ctx.send("Polo!")
      
def setup(bot):
  bot.add_cog(Regex(bot))