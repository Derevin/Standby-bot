import discord
from discord.ext import commands
import re

regex_commands = []

async def regex_handler(message: discord.Message):  
  for trig, resp,flags in regex_commands:    
    if re.search(trig,message.content,flags) != None:
      await resp(message)




async def ayaya_resp(message: discord.Message):
  await message.channel.send("Ayaya!")

com_tuple = ('^ayaya$',ayaya_resp,re.M|re.I)
regex_commands.append(com_tuple)

async def test_resp(message: discord.Message):
  await message.channel.send("Ayaaaaaaaaaaaa!")

com_tuple = ('^testtest$',test_resp,re.M|re.I)
regex_commands.append(com_tuple)