import discord
from discord.ext import commands

async def regex_handler(message: discord.Message):
  await message.channel.send("time to check regex")
