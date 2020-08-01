import discord
import re

regex_songs_commands = []

#### What is love

async def what_is_love_resp(message: discord.Message):
  await message.channel.send('*♬ Baby don\'t hurt me ♬*')
  

regex_songs_commands.append(('^.{0,2}what is .?ove\?{0,3}$', \
  what_is_love_resp,re.M|re.I))
