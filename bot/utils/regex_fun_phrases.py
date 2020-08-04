import discord
import re
import random
import asyncio
from settings import *

regex_fun_phrases_commands = []


### random coin flips


async def coinflip_resp(message: discord.Message):
    await message.channel.send("Heads" if random.randint(0, 1) == 1 else "Tails")


regex_fun_phrases_commands.append(
    ("(coinflip|s a 50[ /]50|(flip|toss) (a |the )?coin)", coinflip_resp, re.M | re.I)
)

### mario


async def mario_resp(message: discord.Message):
    await message.channel.send("Mario!")


regex_fun_phrases_commands.append(
    ("(^| )it(s|'s|s a|'s a|sa) me\\W{0,4}$", mario_resp, re.M | re.I)
)


### uh oh


async def uhoh_resp(message: discord.Message):
    await message.channel.send("SpaghettiOs 😦")
    if random.randint(0, 1) == 1:
        await message.channel.send("..and stinky!")


regex_fun_phrases_commands.append(
    ("^.{0,2}(oh|uh)[ \\-_](oh)\\W{0,4}$", uhoh_resp, re.M | re.I)
)

### ahoy


async def ahoy_resp(message: discord.Message):
    await message.channel.send("Ahoy Matey!")
    if message.guild.id == GUILD_ID:
        await message.add_reaction(":BlobWave:382606234148143115")


regex_fun_phrases_commands.append(("^.{0,2}(ahoy).{0,12}$", ahoy_resp, re.M | re.I))

### spooky


async def spooky_resp(message: discord.Message):
    await message.channel.send("2spooky4me")


regex_fun_phrases_commands.append(("^.{0,12}spooky.{0,12}$", spooky_resp, re.M | re.I))

### wait a min


async def wait_min_resp(message: discord.Message):
    if message.guild.id == GUILD_ID:
        await message.add_reaction(":Thonk:383190394457948181")


regex_fun_phrases_commands.append(
    ("^.{0,2}wait (a )?minute.{0,4}$", wait_min_resp, re.M | re.I)
)

### wednesday


async def wednesday_resp(message: discord.Message):
    await message.channel.send("my dudes")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}It is wednesday\\W{0,4}$", wednesday_resp, re.M | re.I)
)

### tuesday


async def tuesday_resp(message: discord.Message):
    await message.channel.send("Happy <@235055132843180032> appreciation day everyone!")


regex_fun_phrases_commands.append(
    ("^\\W{0,4}It( i|')s tuesday\\W{0,4}$", tuesday_resp, re.M | re.I)
)

### yeee boiiii


async def yeboi_resp(message: discord.Message):
    rsp = "BO" + "I" * (len(message.content) - 1)
    await message.channel.send(rsp)


regex_fun_phrases_commands.append(("^ye{3,50}$", yeboi_resp, re.M | re.I))

### cough bless


async def cough_bless_resp(message: discord.Message):
    await message.channel.send("Bless you!")


regex_fun_phrases_commands.append(
    ("\\*(\\S.*)?(cough|sneeze|acho{2,5})(.*\\S)?\\*", cough_bless_resp, re.M | re.I)
)


### siege backwards


async def egeis_resp(message: discord.Message):
    await message.channel.send("👀?egeiS yas enoemos diD")


regex_fun_phrases_commands.append(("^.*egeis[^\\?]*$", egeis_resp, re.M | re.I))