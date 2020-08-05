import discord
import re
import random
from settings import *

regex_uncategorized_commands = []


async def cough_resp(message: discord.Message):
    await message.channel.send(":mask:")
    await message.channel.send("Wear a mask!")


regex_uncategorized_commands.append(("\\**(cough *){2,}\\**", cough_resp, re.M | re.I))


async def ping_resp(message: discord.Message):
    emoji = discord.utils.get(message.guild.emojis, name="Pingsock")
    if emoji is not None:
        await message.channel.send(emoji)
    await message.channel.send(f"{message.author.mention}")


regex_uncategorized_commands.append((f"{BOT_ID}", ping_resp, re.M | re.I))


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
    if message.content == "||nephew||":
        await message.channel.send("||delet this||")
    else:
        await message.channel.send("delet this")


regex_uncategorized_commands.append(("^\\|*nephew\\|*$", nephew_resp, re.M | re.I))


async def dad_resp(message: discord.Message):
    msg = re.split("m\\W+", message.content, 1)
    if len(re.findall(" ", msg[-1])) < 6:
        await message.channel.send("Hi " + msg[-1] + f", I'm <@{BOT_ID}>.")


regex_uncategorized_commands.append(
    ("^\\.*(i['`´.]?m|i\\.? ?a\\.?m)\\**[ .]{1,4}", dad_resp, re.M | re.I)
)


async def kenobi_resp(message: discord.Message):
    if random.randint(1, 2) == 1:
        await message.channel.send("General " + message.author.mention)
    else:
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/355732809224028161/"
            "628285103902294026/71829918_2663294270370835_6829001011412074496_n.png"
        )


regex_uncategorized_commands.append(("hello there", kenobi_resp, re.M | re.I))


async def spoiler_resp(message: discord.Message):
    if message.content == "||nephew||":
        return
    ignored_channels = ["wf-shitpost", "netflix-and-read", "vie-for-the-vault"]
    responses = ["Hey, what's the big secret?", "What are we whispering about?"]
    if message.channel.name not in ignored_channels:
        await message.channel.send(responses[random.randint(0, len(responses) - 1)])


regex_uncategorized_commands.append(
    ("^(\\|\\|([^\\|]*(\\|[^\\|]+)+|[^\\|]*)\\|\\| *)+$", spoiler_resp, re.M | re.I)
)


async def bell_resp(message: discord.Message):
    await message.channel.send(
        "https://tenor.com/view/hell-hellsbells-acdc-wow-bell-gif-10835118"
    )


regex_uncategorized_commands.append(("ringing my bell", bell_resp, re.M | re.I))


async def no_u_resp(message: discord.Message):
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/731953366015541288/740259703623516170/0vp1zvhnugu21.png"
    )


regex_uncategorized_commands.append(("^no u$", no_u_resp, re.M | re.I))


async def one_of_us_resp(message: discord.Message):
    await message.channel.send("One of us!")


regex_uncategorized_commands.append(
    ("^\\**(one of us(!| |,)*)+\\**$", one_of_us_resp, re.M | re.I)
)


async def society_resp(message: discord.Message):
    await message.channel.send("Bottom Text")


regex_uncategorized_commands.append(
    ("^.{0,5}We live in a society.{0,5}$", society_resp, re.M | re.I)
)


async def deep_one_resp(message: discord.Message):
    await message.channel.send(
        "blub blub blub blub blub blub blub blub blub blub blub blub blub blub blub"
    )


regex_uncategorized_commands.append(
    ("^if I (were|was) a deep one", deep_one_resp, re.M | re.I)
)


async def sixtynine_resp(message: discord.Message):
    await message.add_reaction("🇳")
    await message.add_reaction("🇮")
    await message.add_reaction("🇨")
    await message.add_reaction("🇪")


regex_uncategorized_commands.append(
    ("^[^\\/<]*69(([^1][^1]).*|[^1].|.[^1]|.?)$", sixtynine_resp, re.M | re.I)
)


async def woop_resp(message: discord.Message):
    await message.channel.send("That's the sound of da police!")


regex_uncategorized_commands.append(("^woop woop[\\.!]*$", woop_resp, re.M | re.I))


async def paragon_resp(message: discord.Message):
    await message.channel.send("Fuck Epic!")


regex_uncategorized_commands.append(("paragon", paragon_resp, re.M | re.I))


async def bruh_resp(message: discord.Message):
    bruh = await message.channel.send(
        "https://cdn.discordapp.com/attachments/"
        "367037496455856128/654732909718274061/"
        "74661755_2772995016045496_4416748817345413120_n.jpg"
    )
    await bruh.add_reaction("🅱️")
    await bruh.add_reaction("🇷")
    await bruh.add_reaction("🇺")
    await bruh.add_reaction("🇭")


regex_uncategorized_commands.append(("^\\W*bruh\\W*$", bruh_resp, re.M | re.I))


async def dad_reclaim_resp(message: discord.Message):
    await message.channel.send("Oi, that's my job!")


regex_uncategorized_commands.append(
    ("^Hi\\W+.*I(m|'m| am).{0,20}$", dad_reclaim_resp, re.M | re.I)
)


async def hans_resp(message: discord.Message):
    await message.channel.send("Get ze flammenwerfer!")


regex_uncategorized_commands.append(("^hans\\W*$", hans_resp, re.M | re.I))


async def loli_resp(message: discord.Message):
    glare = discord.utils.get(message.guild.emojis, name="BlobGlare")
    if glare is not None:
        await message.channel.send(glare)
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/413861431906402334/731636158223614113/image0-27.jpg"
    )
    if re.search("loIi", message.content) is not None:
        await message.channel.send(f"Fuck off, {message.author.mention}")


regex_uncategorized_commands.append(("lo[lI]i", loli_resp, re.M | re.I))


async def dont_at_me_resp(message: discord.Message):
    await message.channel.send(f"{message.author.mention}")


regex_uncategorized_commands.append(
    ("do[ ]?n[ ']?t @ me", dont_at_me_resp, re.M | re.I)
)


async def america_resp(message: discord.Message):
    await message.channel.send("Fuck yeah!")


regex_uncategorized_commands.append(
    ("^\\W*a?'?m(e|u)rica\\W*$", america_resp, re.M | re.I)
)

