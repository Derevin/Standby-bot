import json

import nextcord
import requests
from nextcord.ext import commands
from settings import *


class GPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command()
    async def voidgpt(self, interaction, prompt):
        await interaction.response.defer()
        resp = requests.request(
            "POST",
            url="https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": f"{prompt}"}],
            },
        )
        try:
            resp = json.loads(resp.content.decode("utf-8"))
            full_message = resp["choices"][0]["message"]["content"].split(" ")
            message = []
            for word in full_message:
                message.append(word)
                if len(" ".join(message)) > 2000:
                    await interaction.send(" ".join(message[:-1]))
                    message = [message[-1]]
            await interaction.send(" ".join(message))
        except KeyError:
            await interaction.send("No response", ephemeral=True)


def setup(bot):
    bot.add_cog(GPT(bot))
