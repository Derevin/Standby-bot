import discord
import re
import random

regex_uncategorized_commands = []


async def cough_resp(message: discord.Message):
    await message.channel.send(":mask:")
    await message.channel.send("Wear a mask!")


regex_uncategorized_commands.append(("\\**(cough *){2,}\\**", cough_resp, re.M | re.I))


async def ping_resp(message: discord.Message):
    await message.channel.send("<:Pingsock:739930335420088411>")


regex_uncategorized_commands.append(("738113308787343462", ping_resp, re.M | re.I))


async def uwu_resp(message: discord.Message):
    msg = message.content
    if re.search(":[^ ]*(o|u|0|O|U)[wvWV](o|u|0|O|U)[^ ]*:", msg) is not None:
        return

    n = len(re.findall("[rRlL]", msg))
    txt = "https://www.youtube.com/watch?v=rrD3jp34BFg"
    if n > 4:
        txt = re.sub("[rRlL]", "w", msg)
    elif random.randint(1, 10) == 7:
        txt = "I'll let you off with just a warning this time but I'd better not see you doing it again."
    await message.channel.send(txt)


regex_uncategorized_commands.append(
    ("^[^\\/]*(o|u|0)[wv](o|u|0).*$", uwu_resp, re.M | re.I)
)


async def nephew_resp(message: discord.Message):
    await message.channel.send("delet this")


regex_uncategorized_commands.append(("nephew", nephew_resp, re.M | re.I))


async def dad_resp(message: discord.Message):
    msg = re.split("m\\W+", message.content, 1)
    if len(re.findall(" ", msg[-1])) < 6:
        await message.channel.send("Hi " + msg[-1] + ", I'm <@738113308787343462>.")


regex_uncategorized_commands.append(
    ("^\\.*(i['`´.]?m|i\\.? ?a\\.?m)\\**[ .]{1,4}", dad_resp, re.M | re.I)
)


async def kenobi_resp(message: discord.Message):
    if random.randint(1, 2) == 1:
        await message.channel.send("General " + message.author.mention)
    else:
        await message.channel.send(
            """https://cdn.discordapp.com/attachments/355732809224028161/
            628285103902294026/71829918_2663294270370835_6829001011412074496_n.png"""
        )


regex_uncategorized_commands.append(("hello there", kenobi_resp, re.M | re.I))
