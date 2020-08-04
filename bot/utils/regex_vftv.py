import discord
import re
import random
import asyncio

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
    if message.author.id == 235055132843180032:
        reactions = [
            ":BlobWave:382606234148143115",
            "🇭",
            "🇮",
            ":BlobGuns:388081474760605706",
            "🇸",
            "🇱",
            "🇦",
            "🇻",
            "🇪",
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
    await message.channel.send("Quickly, <@168350377824092160>, quickly!")
    await message.add_reaction("👏")


regex_vftv_commands.append(
    (
        "^.*((\\[Stradavar Prime\\])|(:StradavarPrime.{0,4}:)).*$",
        stradavar_resp,
        re.M | re.I,
    )
)
