import nextcord
import re
import random
import asyncio
from settings import *

regex_vftv_commands = []


### pinging people


async def pingsock_resp(bot, message: nextcord.Message):
    await asyncio.sleep(5)
    if random.randint(1, 4) == 1:
        await message.channel.send(
            f"Do I see someone who loves being pinged, {message.author.mention}?"
        )


regex_vftv_commands.append(
    ("^<:Pingsock:421725383172554753>$", pingsock_resp, re.M | re.I)
)

### waving at people


async def wave_resp(bot, message: nextcord.Message):
    if message.author.id == FEL_ID:
        reactions = [
            ":BlobWave:382606234148143115",
            "🇫",
            "🇪",
            "🇱",
            "❤️",
            "🇨",
            "🇭",
            "🇦",
            "🇳",
            ":BlobAww:380182813300752395",
        ]
        for x in reactions:
            await message.add_reaction(x)
    elif ":Whale" not in message.content:
        await message.add_reaction(":BlobWave:382606234148143115")


regex_vftv_commands.append(
    (
        """^(<:BlobWave:382606234148143115>|<:BlobCoffee:456004868990173198>)""",
        wave_resp,
        re.M | re.I,
    )
)

### Pedestal


async def pedestal_resp(bot, message: nextcord.Message):
    await message.add_reaction("👏")
    await message.channel.send("Quickly, master <@235055132843180032>, quickly!")


regex_vftv_commands.append(
    ("(\\[Pedestal Prime\\])|(:PedestalPrime:)", pedestal_resp, re.M | re.I)
)


### Kross Wood


async def wood_resp(bot, message: nextcord.Message):
    if message.author.id == 255653858095661057:
        await message.add_reaction("🪓")
        await message.add_reaction("🌲")


regex_vftv_commands.append(("wood", wood_resp, re.M | re.I))

### stradavar


async def stradavar_resp(bot, message: nextcord.Message):
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


async def keto_resp(bot, message: nextcord.Message):
    if (
        message.channel.name == "awww"
        and message.author.id == 421039678481891348
        and len(message.attachments) > 0
        and message.attachments[0].height is not None
    ):
        await message.add_reaction(":ketoroll:634859950283161602")
        await message.add_reaction(":ketoface:634852360514174976")


regex_vftv_commands.append((".*", keto_resp, re.M | re.I))

### Siege?


async def siegeQ_resp(bot, message: nextcord.Message):
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


async def offers_resp(bot, message: nextcord.Message):
    if message.channel.name != "offers":
        return

    whitelist = [
        "https",
        "store",
        "steam",
        "free",
        "epic",
        "EGS",
        "launcher",
        "percent",
        "%",
        "uplay",
        "origin",
        "GOG",
        "ubi",
        "key",
        "code",
        "sale",
    ]

    if (
        any([word in message.content.lower() for word in whitelist])
        or len(message.attachments) > 0
    ):
        return

    await message.delete()
    await message.author.send(
        f"Hi {message.author.mention}! We're trying to streamline {message.channel.mention} - please update "
        "your post to contain a link, an image, or a specific reference to a game store and re-post it. "
        "If you've received this message in error, please contact your favorite mod."
    )


regex_vftv_commands.append((".*", offers_resp, re.M | re.I))

### #streams


async def streams_resp(bot, message: nextcord.Message):
    if (
        message.channel.name == "community-streams"
        and "twitch.tv" not in message.content
    ):
        await message.delete()
        await message.author.send(
            f"Hi {message.author.mention}! We're keeping {message.channel.mention} reserved for stream posts - "
            "please update your post to contain a twitch link and re-post it. "
            "If you've received this message in error, please contact your favorite mod."
        )


regex_vftv_commands.append((".*", streams_resp, re.M | re.I))


## GOOD/BAD bot


async def good_bot_resp(bot, message: nextcord.Message):
    await message.add_reaction(":BlobAww:380182813300752395")


regex_vftv_commands.append(
    (
        r"^(.{0,20} |)(good|thanks?( (yo)?u)?|love( (yo)?u)?) (bot|<..736265509951242403>)\W{0,2}$",
        good_bot_resp,
        re.M | re.I,
    )
)


async def bad_bot_resp(bot, message: nextcord.Message):
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


async def hms_resp(bot, message: nextcord.Message):
    await message.channel.send(GIT_STATIC_URL + "/images/hms%20fucking.png")


regex_vftv_commands.append(("welcome aboard the hms fucking", hms_resp, re.M | re.I))


async def gramps_resp(bot, message: nextcord.Message):
    await message.channel.send(GIT_STATIC_URL + "/images/markus.gif")
    await message.channel.send(message.content)


regex_vftv_commands.append((r"^<@!?141523991260037120>$", gramps_resp, re.M | re.I))
