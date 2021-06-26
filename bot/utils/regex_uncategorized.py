import discord
import re
import random
import aiohttp
import asyncio
from settings import *
from settings_files.warframe_data import mod_list
from utils.util_functions import *

regex_uncategorized_commands = []
clean_links = []


async def cough_resp(bot, message: discord.Message):
    await message.channel.send(":mask:")
    await message.channel.send("Wear a mask!")


regex_uncategorized_commands.append(("\\**(cough *){2,}\\**", cough_resp, re.M | re.I))


async def ping_resp(bot, message: discord.Message):
    emoji = discord.utils.get(message.guild.emojis, name="Pingsock")
    if emoji is not None:
        await message.channel.send(emoji)
    await message.channel.send(f"{message.author.mention}")


regex_uncategorized_commands.append((f"{BOT_ID}", ping_resp, re.M | re.I))


async def uwu_resp(bot, message: discord.Message):
    msg = message.content
    whitelist = [
        r":[^ ]*(o|u|0|O|U)[wvWV](o|u|0|O|U)[^ ]*:",
        "lenovo",
        "coworker",
        "kosovo",
    ]

    for word in whitelist:
        if re.search(word, msg, re.I) is not None:
            return

    n = len(re.findall("[rRlL]", msg))
    txt = "https://www.youtube.com/watch?v=rrD3jp34BFg"
    if n > 4:
        txt = re.sub("[rRlL]", "w", msg)
    elif random.randint(1, 10) == 7:
        txt = "I'll let you off with just a warning this time but I'd better not see you doing it again."
    await message.channel.send(txt)


regex_uncategorized_commands.append((r"^[^\/]*(o|u|0)[wv]\1.*$", uwu_resp, re.M | re.I))


async def nephew_resp(bot, message: discord.Message):
    if message.content == "||nephew||":
        await message.channel.send("||delet this||")
    else:
        await message.channel.send("delet this")


regex_uncategorized_commands.append(("^\\|*nephew\\|*$", nephew_resp, re.M | re.I))


# async def dad_resp(bot, message: discord.Message):
#     msg = re.split("m ", message.content, 1)
#     if len(re.findall(" ", msg[-1])) < 6:
#         await message.channel.send("Hi " + msg[-1] + f", I'm <@{BOT_ID}>.")


# regex_uncategorized_commands.append(
#     ("^\\.*(i['`´.]?m|i\\.? ?a\\.?m)\\**[ .]{1,4}", dad_resp, re.M | re.I)
# )


async def kenobi_resp(bot, message: discord.Message):
    if random.randint(1, 2) == 1:
        await message.channel.send("General " + message.author.mention)
    else:
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/355732809224028161/"
            "628285103902294026/71829918_2663294270370835_6829001011412074496_n.png"
        )


regex_uncategorized_commands.append(("hello there", kenobi_resp, re.M | re.I))


# async def spoiler_resp(bot, message: discord.Message):
#     if message.content == "||nephew||":
#         return
#     ignored_channels = ["wf-shitpost", "netflix-and-read", "vie-for-the-vault"]
#     responses = ["Hey, what's the big secret?", "What are we whispering about?"]
#     if message.channel.name not in ignored_channels:
#         await message.channel.send(responses[random.randint(0, len(responses) - 1)])


# regex_uncategorized_commands.append(
#     ("^(\\|\\|([^\\|]*(\\|[^\\|]+)+|[^\\|]*)\\|\\| *)+$", spoiler_resp, re.M | re.I)
# )


async def bell_resp(bot, message: discord.Message):
    await message.channel.send(
        "https://tenor.com/view/hell-hellsbells-acdc-wow-bell-gif-10835118"
    )


regex_uncategorized_commands.append(("ringing my bell", bell_resp, re.M | re.I))


async def no_u_resp(bot, message: discord.Message):
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/731953366015541288/740259703623516170/0vp1zvhnugu21.png"
    )


regex_uncategorized_commands.append(("^no u$", no_u_resp, re.M | re.I))


async def one_of_us_resp(bot, message: discord.Message):
    await message.channel.send("One of us!")


regex_uncategorized_commands.append(
    ("^\\**(one of us(!| |,)*)+\\**$", one_of_us_resp, re.M | re.I)
)


async def society_resp(bot, message: discord.Message):
    await message.channel.send("Bottom Text")


regex_uncategorized_commands.append(
    ("^.{0,5}We live in a society.{0,5}$", society_resp, re.M | re.I)
)


async def deep_one_resp(bot, message: discord.Message):
    await message.channel.send(
        "blub blub blub blub blub blub blub blub blub blub blub blub blub blub blub"
    )


regex_uncategorized_commands.append(
    ("^if I (were|was) a deep one", deep_one_resp, re.M | re.I)
)


async def sixtynine_resp(bot, message: discord.Message):
    await message.add_reaction("🇳")
    await message.add_reaction("🇮")
    await message.add_reaction("🇨")
    await message.add_reaction("🇪")


regex_uncategorized_commands.append(
    ("^[^\\/<]*69(([^1][^1]).*|[^1].|.[^1]|.?)$", sixtynine_resp, re.M | re.I)
)


async def fourtwenty_resp(bot, message: discord.Message):
    await message.add_reaction("🔥")
    await message.add_reaction("🇧")
    await message.add_reaction("🇱")
    await message.add_reaction("🇦")
    await message.add_reaction("🇿")
    await message.add_reaction("🇪")
    await message.add_reaction("🇮")
    await message.add_reaction("🇹")


regex_uncategorized_commands.append(("^[^\\/<]*420", fourtwenty_resp, re.M | re.I))


async def woop_resp(bot, message: discord.Message):
    await message.channel.send("That's the sound of da police!")


regex_uncategorized_commands.append(("^woop woop[\\.!]*$", woop_resp, re.M | re.I))


async def paragon_resp(bot, message: discord.Message):
    await message.channel.send("Fuck Epic!")


regex_uncategorized_commands.append(("paragon", paragon_resp, re.M | re.I))


async def bruh_resp(bot, message: discord.Message):
    bruh = await message.channel.send(
        "https://cdn.discordapp.com/attachments/"
        "376031149371162635/746081315270426704/unknown.png"
    )
    await bruh.add_reaction("🅱️")
    await bruh.add_reaction("🇷")
    await bruh.add_reaction("🇺")
    await bruh.add_reaction("🇭")


regex_uncategorized_commands.append(("^\\W*bruh\\W*$", bruh_resp, re.M | re.I))


async def dad_reclaim_resp(bot, message: discord.Message):
    await message.channel.send("Oi, that's my job!")
    await message.channel.send("Well, it used to be, at least...")


regex_uncategorized_commands.append(
    ("^Hi\\W+.*I(m|'m| am) .{0,30}$", dad_reclaim_resp, re.M | re.I)
)


async def hans_resp(bot, message: discord.Message):
    await message.channel.send("Get ze Flammenwerfer!")


regex_uncategorized_commands.append(("^hans\\W*$", hans_resp, re.M | re.I))


async def loli_resp(bot, message: discord.Message):
    if message.author.id == JORM_ID or re.search("http", message.content, re.I):
        return
    glare = discord.utils.get(message.guild.emojis, name="BlobGlare")
    if glare is not None:
        await message.add_reaction(glare)
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/413861431906402334/731636158223614113/image0-27.jpg"
    )
    if re.search("loli", message.content, re.I) is None:
        await message.channel.send(f"Fuck off, {message.author.mention}")


regex_uncategorized_commands.append(("(^|\\W)[LlI|][Oo0][LlI|][Ii]", loli_resp, re.M))


async def dont_at_me_resp(bot, message: discord.Message):
    await message.channel.send(f"{message.author.mention}")


regex_uncategorized_commands.append(
    ("do[ ]?n[o ']?t (@|at) me", dont_at_me_resp, re.M | re.I)
)


async def america_resp(bot, message: discord.Message):
    await message.channel.send("Fuck yeah!")


regex_uncategorized_commands.append(
    ("^\\W*a?'?m(e|u)rica\\W*$", america_resp, re.M | re.I)
)


async def mod_resp(bot, message: discord.Message):
    mod_names = re.findall(r"(?<=\[)[a-zA-Z ']+(?=\])", message.content)
    for mod_name in mod_names:
        if mod_name.lower() in mod_list:
            await message.channel.send(mod_list[mod_name.lower()])


regex_uncategorized_commands.append((r"\[.*\]", mod_resp, re.M | re.I))


async def x_is_x_resp(bot, message: discord.Message):
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/744224801429782679/760882040492523530/X_is_X.png"
    )


regex_uncategorized_commands.append(
    (r"^(.* )?(\w+) (is|are) \2(\W.{0,5})?$", x_is_x_resp, re.M | re.I)
)


async def tree_fiddy_resp(bot, message: discord.Message):
    await message.add_reaction("🐍")


regex_uncategorized_commands.append(("tree fiddy", tree_fiddy_resp, re.M | re.I))


async def cluttered_link_resp(bot, message: discord.Message):

    link = re.search(
        r"(https:\/\/\w+\.\w+\.\w+.+)\?(\w+=\D+&?)+", message.content
    ).group(1)
    whitelist = ["youtube", "spotify"]

    if any(exception in link for exception in whitelist):
        return

    ree = get_emoji(message.channel.guild, "FEELSREEE")
    if ree:
        await message.channel.send(ree)

    await message.channel.send("Clean up your links REEE")

    clean_links.append(link)
    await asyncio.sleep(60)
    if link in clean_links:
        clean_links.remove(link)


regex_uncategorized_commands.append(
    (r"https:\/\/\w+\.\w+\.\w+.+\?(\w+=\D+&?)+", cluttered_link_resp, re.M | re.I)
)


async def clean_link_resp(bot, message: discord.Message):
    for link in clean_links:
        if link in message.content:
            await message.channel.send("Thank you.")
            clean_links.remove(link)
            break


regex_uncategorized_commands.append((r"https:", clean_link_resp, re.M | re.I))

