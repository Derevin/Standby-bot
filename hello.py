import discord
from discord.ext import commands

client = commands.Bot(command_prefix = ',')

@client.event
async def on_ready():
  print('Bot is ready.')

client.run('NzM2MjY1NTA5OTUxMjQyNDAz.XxsSsA.PQjkf-T6_A1_zzHG85KDn-3Qdqk')


