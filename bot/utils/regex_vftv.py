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
    if random.randint(0, 99) < 100:
        await message.add_reaction(":BlobWave:382606234148143115")


regex_vftv_commands.append(
    (
        """^(<:BlobWave:382606234148143115> ?(<:BlobCoffee:456004868990173198>)?|
        <:BlobCoffee:456004868990173198> ?(<:BlobWave:382606234148143115>)?)$""",
        wave_resp,
        re.M | re.I,
    )
)
