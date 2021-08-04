import discord
import re
import random
import asyncio
import datetime
from settings import *

regex_fun_phrases_commands = []


### random coin flips


async def coinflip_resp(bot, message: discord.Message):
    await message.channel.send("Heads" if random.randint(0, 1) == 1 else "Tails")


regex_fun_phrases_commands.append(
    ("(coinflip|s a 50[ /]50|(flip|toss) (a |the )?coin)", coinflip_resp, re.M | re.I)
)

### mario


async def mario_resp(bot, message: discord.Message):
    await message.channel.send("Mario!")


regex_fun_phrases_commands.append(
    (r"(^| )it(s|'s|s a|'s a|sa) me\W{0,4}$", mario_resp, re.M | re.I)
)


### uh oh


async def uhoh_resp(bot, message: discord.Message):
    await message.channel.send("SpaghettiOs 😦")
    if random.randint(0, 1) == 1:
        await message.channel.send("..and stinky!")


regex_fun_phrases_commands.append(
    ("^.{0,2}(oh|uh)[ \\-_](oh)\\W{0,4}$", uhoh_resp, re.M | re.I)
)

### ahoy


async def ahoy_resp(bot, message: discord.Message):
    await message.channel.send("Ahoy Matey!")
    if message.guild.id == GUILD_ID:
        await message.add_reaction(":BlobWave:382606234148143115")


regex_fun_phrases_commands.append(("^.{0,2}(ahoy).{0,12}$", ahoy_resp, re.M | re.I))

### spooky


async def spooky_resp(bot, message: discord.Message):
    await message.channel.send("2spooky4me")


regex_fun_phrases_commands.append(("^.{0,12}spooky.{0,12}$", spooky_resp, re.M | re.I))

### wait a min


async def wait_min_resp(bot, message: discord.Message):
    if message.guild.id == GUILD_ID:
        await message.add_reaction(":Thonk:383190394457948181")


regex_fun_phrases_commands.append(
    ("^.{0,2}wait (a )?minute.{0,4}$", wait_min_resp, re.M | re.I)
)

### wednesday


async def wednesday_resp(bot, message: discord.Message):
    await message.channel.send("my dudes")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}It is wednesday\\W{0,4}$", wednesday_resp, re.M | re.I)
)


async def mittwoch_resp(bot, message: discord.Message):
    await message.channel.send("meine Kerle")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}Es ist Mittwoch\\W{0,4}$", mittwoch_resp, re.M | re.I)
)


async def sroda_resp(bot, message: discord.Message):
    await message.channel.send("o panowie")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}jest [sś]roda\\W{0,4}$", sroda_resp, re.M | re.I)
)


async def woensdag_resp(bot, message: discord.Message):
    await message.channel.send("mijn makkers")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}het is woensdag\\W{0,4}$", woensdag_resp, re.M | re.I)
)


async def szerda_resp(bot, message: discord.Message):
    await message.channel.send("felebarátaim")
    await message.channel.send("ááááááááááÁÁÁÁÁÁÁÁÁÁ**ÁÁÁÁÁ**")


regex_fun_phrases_commands.append(
    ("^.{0,4}szerda van\\W{0,4}$", szerda_resp, re.M | re.I)
)


async def streda_resp(bot, message: discord.Message):
    await message.channel.send("kamoši moji")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}je streda\\W{0,4}$", streda_resp, re.M | re.I)
)


async def srida_resp(bot, message: discord.Message):
    await message.channel.send("moji ljudi")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}sr(e|i(je)?)da je\\W{0,4}$", srida_resp, re.M | re.I)
)


async def mercredi_resp(bot, message: discord.Message):
    await message.channel.send("mes mecs")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}c'?est mercredi\\W{0,4}$", mercredi_resp, re.M | re.I)
)


async def keskiviikko_resp(bot, message: discord.Message):
    await message.channel.send("kaverit")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}se on keskiviikko\\W{0,4}$", keskiviikko_resp, re.M | re.I)
)


async def onsdag_resp(bot, message: discord.Message):
    await message.channel.send("mina bekanta")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}det är (ons|fre)dag\\W{0,4}$", onsdag_resp, re.M | re.I)
)


async def suiyobi_resp(bot, message: discord.Message):
    await message.channel.send("お前ら")
    await message.channel.send("ああああああ**ああああ**")


regex_fun_phrases_commands.append(("^.{0,4}水曜日だ\\W{0,4}$", suiyobi_resp, re.M | re.I))


async def onsdag_resp_no(bot, message: discord.Message):
    await message.channel.send("folkens")
    await message.channel.send("ææææææææææÆÆÆÆÆÆÆÆÆÆ**ÆÆÆÆÆ**")


regex_fun_phrases_commands.append(
    ("^.{0,4}det er onsdag\\W{0,4}$", onsdag_resp_no, re.M | re.I)
)


async def miercoles_resp(bot, message: discord.Message):
    await message.channel.send("mis amigos")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}es mi(e|é)rcoles\\W{0,4}$", miercoles_resp, re.M | re.I)
)


async def miercuri_resp(bot, message: discord.Message):
    await message.channel.send("fraţii mei")
    await message.channel.send("aaaaaaaaaaAAAAAAAAAA**AAAAA**")


regex_fun_phrases_commands.append(
    ("^.{0,4}este miercuri\\W{0,4}$", miercuri_resp, re.M | re.I)
)


async def reviee_resp(bot, message: discord.Message):
    await message.channel.send("אחים שלי")
    await message.channel.send("אאאאאאאאאאאאאאאאה")


regex_fun_phrases_commands.append(
    ("^.{0,4}היום יום רביעי\\W{0,4}$", reviee_resp, re.M | re.I)
)

### tuesday


async def tuesday_resp(bot, message: discord.Message):
    await message.channel.send("Happy <@235055132843180032> appreciation day everyone!")


regex_fun_phrases_commands.append(
    ("^\\W{0,4}It( i|')s tuesday\\W{0,4}$", tuesday_resp, re.M | re.I)
)

### yeee boiiii


async def yeboi_resp(bot, message: discord.Message):
    rsp = "BO" + "I" * (len(message.content) - 1)
    if len(rsp) > 2000:
        rsp = rsp[:1999]
    await message.channel.send(rsp)


regex_fun_phrases_commands.append(("^ye{3,}$", yeboi_resp, re.M | re.I))

### cough bless


async def cough_bless_resp(bot, message: discord.Message):
    await message.channel.send("Bless you!")


regex_fun_phrases_commands.append(
    ("\\*(\\S.*)?(cough|sneeze|acho{2,5})(.*\\S)?\\*", cough_bless_resp, re.M | re.I)
)


### siege backwards


async def egeis_resp(bot, message: discord.Message):
    await message.channel.send("👀?egeiS yas enoemos diD")


regex_fun_phrases_commands.append(("^.*egeis[^\\?]*$", egeis_resp, re.M | re.I))


### fuck me


async def fme_resp(bot, message: discord.Message):
    await message.channel.send("Don't mind if I do 👍")


regex_fun_phrases_commands.append(("^.{0,2}fuck me\\W{0,4}$", fme_resp, re.M | re.I))

############ ayaya regex


async def ayaya_resp(bot, message: discord.Message):
    await message.channel.send("Ayaya!")
    if message.guild.id == GUILD_ID:
        await message.add_reaction(":Ayy:610479153937907733")
        await message.add_reaction(":Ayy2:470743166207787010")


regex_fun_phrases_commands.append(("^ayaya\\W{0,4}$", ayaya_resp, re.M | re.I))
