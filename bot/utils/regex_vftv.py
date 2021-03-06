import discord
import re
import random
import asyncio
from settings import *

regex_vftv_commands = []


### pinging people


async def pingsock_resp(message: discord.Message):
    await asyncio.sleep(5)
    if random.randint(1, 4) == 1:
        await message.channel.send(
            f"Do I see someone who loves being pinged, {message.author.mention}?"
        )


regex_vftv_commands.append(
    ("^<:Pingsock:421725383172554753>$", pingsock_resp, re.M | re.I)
)

### waving at people


async def wave_resp(message: discord.Message):
    if message.author.id == FEL_ID:
        reactions = [
            ":BlobWave:382606234148143115",
            "🇭",
            "🇮",
            ":BlobGuns:388081474760605706",
            "🇫",
            "🇪",
            "🇱",
            ":BlobAww:380182813300752395",
        ]
        for x in reactions:
            await message.add_reaction(x)
    elif random.randint(0, 99) < 45:
        await message.add_reaction(":BlobWave:382606234148143115")


regex_vftv_commands.append(
    (
        """^(<:BlobWave:382606234148143115> ?(<:BlobCoffee:456004868990173198>)?|
        <:BlobCoffee:456004868990173198> ?(<:BlobWave:382606234148143115>)?)$""",
        wave_resp,
        re.M | re.I,
    )
)

### Pedestal


async def pedestal_resp(message: discord.Message):
    await message.add_reaction("👏")
    await message.channel.send("Quickly, master <@235055132843180032>, quickly!")


regex_vftv_commands.append(
    ("(\\[Pedestal Prime\\])|(:PedestalPrime:)", pedestal_resp, re.M | re.I)
)


### Kross Wood


async def wood_resp(message: discord.Message):
    if message.author.id == 255653858095661057:
        await message.add_reaction(":Chainsaw:621096339207618565")
        await message.add_reaction("🌲")


regex_vftv_commands.append(("wood", wood_resp, re.M | re.I))

### stradavar


async def stradavar_resp(message: discord.Message):
    await message.channel.send(f"Quickly, <@{JORM_ID}>, quickly!")
    await message.add_reaction("👏")


regex_vftv_commands.append(
    (
        "^.*((\\[Stradavar Prime\\])|(:StradavarPrime.{0,4}:)).*$",
        stradavar_resp,
        re.M | re.I,
    )
)

### Keto


async def keto_resp(message: discord.Message):
    if (
        message.channel.name == "awww"
        and message.author.id == 421039678481891348
        and len(message.attachments) > 0
        and message.attachments[0].height is not None
    ):
        await message.add_reaction(":ketoroll:634859950283161602")
        await message.add_reaction(":ketoface:634852360514174976")


regex_vftv_commands.append((".*", keto_resp, re.M | re.I))

### Hek


async def hek_resp(message: discord.Message):
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/731953366015541288/731953566658592888/med_1528926166_image.png"
    )


regex_vftv_commands.append(("^look\\W*brothers?\\W*$", hek_resp, re.M | re.I))

### Siege?


async def siegeQ_resp(message: discord.Message):
    reactions = [
        "⏰",
        "2️⃣",
        ":GlobCatGun:621700315376517122",
        "🇸",
        "🇹",
        "🇷",
        "🇴",
        "🇳",
        "🇿",
        "0️⃣",
    ]
    for x in reactions:
        await message.add_reaction(x)


regex_vftv_commands.append(("siege.*\\?", siegeQ_resp, re.M | re.I))


### #offers


async def offers_resp(message: discord.Message):
    if message.channel.name != "offers":
        return
    if (
        re.search(
            "https|store|steam|free|epic|EGS|launcher|percent|%|uplay|origin|GOG|ubi",
            message.content,
        )
        is None
        and len(message.attachments) == 0
    ):
        await message.delete()
        await message.author.send(
            f"Hi {message.author.mention}! We're trying to streamline {message.channel.mention} - please update "
            "your post to contain a link, an image, or a specific reference to a game store and re-post it. "
            "If you've received this message in error, please contact your favorite mod."
        )


regex_vftv_commands.append((".*", offers_resp, re.M | re.I))


async def pp_resp(message: discord.Message):
    await message.channel.send(f"Just like <@{JORM_ID}>'s pp")


regex_vftv_commands.append(
    (
        "(so|really|very|pretty|it[ 'i]*s) (tiny|small|smol|puny)\\W*$",
        pp_resp,
        re.M | re.I,
    )
)


## GOOD/BAD bot


async def good_bot_resp(message: discord.Message):
    await message.add_reaction(":BlobAww:380182813300752395")


regex_vftv_commands.append(
    (
        r"^(.{0,20} |)(good|thanks?( (yo)?u)?|love( (yo)?u)?) (bot|<..736265509951242403>)\W{0,2}$",
        good_bot_resp,
        re.M | re.I,
    )
)


async def bad_bot_resp(message: discord.Message):
    await message.add_reaction(":BlobBan:438000257385889792")


regex_vftv_commands.append(
    (
        r"^(.{0,20} |)"
        r"((bad)|(stupid)|(f((uc)?k)? off)|(fuck)|(hate ((yo)?u|this))|(shut up)|(stfu)|(f((uc)?k)? ?(yo)?u)) "
        r"((void )?bot|<..736265509951242403>).*$",
        bad_bot_resp,
        re.M | re.I,
    )
)


async def hms_resp(message: discord.Message):
    await message.channel.send(
        "https://cdn.discordapp.com/attachments/744224801429782679/806231697728995358/unknown.png"
    )


regex_vftv_commands.append(("welcome aboard the hms fucking", hms_resp, re.M | re.I))

