import aiohttp
from nextcord.ext import commands
import nextcord
from nextcord import Interaction, SlashOption
import random
from settings import *


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Posts a random animal image")
    async def animal(
        self,
        interaction: Interaction,
        animal=SlashOption(
            description="Choose a type of animal",
            choices={"Cat", "Dog", "Fox"},
        ),
    ):
        args = {
            "Cat": (
                "https://api.thecatapi.com/v1/images/search?size=full",
                "Meow",
                "https://thecatapi.com",
                "url",
            ),
            "Dog": (
                "https://dog.ceo/api/breeds/image/random",
                "Woof",
                "https://dog.ceo",
                "message",
            ),
            "Fox": (
                "https://randomfox.ca/floof/",
                "What does the fox say",
                "https://randomfox.ca",
                "image",
            ),
        }
        api_url, title, url, json_key = args[animal]
        async with aiohttp.ClientSession() as cs:
            async with cs.get(api_url) as r:

                data = await r.json()
                if type(data) != dict:
                    data = data[0]

                embed = nextcord.Embed(title=title)
                embed.set_image(url=data[json_key])
                embed.set_footer(text=url)

                await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(Animals(bot))
