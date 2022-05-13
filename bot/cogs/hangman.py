import asyncio
from nextcord.ext import commands
import nextcord
from nextcord import Interaction, SlashOption
import re
import random
from settings import *
from utils.util_functions import *

image_links = [GIT_STATIC_URL + f"/images/Hangman-{num}.png" for num in range(7)]


class HangmanGame:
    def __init__(self):
        self.status = "Inactive"
        self.lock = asyncio.Lock()

    def create_embed(self):

        embed = nextcord.Embed(color=PALE_GREEN)
        title = re.sub(" ", "   ", self.progress)
        title = re.sub("_", r"\_ ", title)
        title = re.sub(r"(\w)", r"\1 ", title)
        embed.title = title if len(self.wrong_guesses) < 6 else self.word
        if len(self.wrong_guesses) >= 6:
            desc = "Game over! Use `/hangman` to start another round."
        elif self.word == self.progress:
            desc = "Game won! Use `/hangman` to start another round."
        else:
            desc = "Welcome to Void Hangman! Use `/hangman` to guess a letter or the whole word/phrase."
        embed.description = desc
        embed.set_image(url=image_links[len(self.wrong_guesses)])
        embed.add_field(
            name="Wrong guesses",
            value="None"
            if len(self.wrong_guesses) == 0
            else ", ".join(self.wrong_guesses),
            inline=False,
        )
        return embed

    def setup(self, word, host, channel):

        self.status = "Active"
        self.word = word.upper()
        self.progress = re.sub(r"\w", "_", self.word)
        self.wrong_guesses = []
        self.host = host
        self.channel = channel
        self.embed = self.create_embed()

    def check_letter(self, letter):
        letter = letter.upper()
        if letter in self.word:
            for match in re.finditer(letter, self.word):
                self.progress = (
                    self.progress[: match.start()]
                    + letter
                    + self.progress[match.start() + 1 :]
                )
            self.embed = self.create_embed()
            return True
        else:
            self.wrong_guesses.append(letter)
            self.embed = self.create_embed()
            return False

    def check_word(self, word):
        word = word.upper()
        if word == self.word:
            self.progress = word
            self.embed = self.create_embed()
            return True
        else:
            self.wrong_guesses.append(word)
            self.embed = self.create_embed()
            return False

    def state(self):
        if len(self.wrong_guesses) == 6:
            return "Game Over"
        elif self.progress == self.word:
            return "Game Won"
        else:
            return "Still guessing"


game = HangmanGame()


class Hangman(commands.Cog, name="Void Hangman"):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[GUILD_ID])
    async def hangman():
        pass

    @hangman.subcommand(description="Start a game of Void Hangman")
    async def start(
        self,
        interaction: Interaction,
        phrase=SlashOption(
            description="The word or phrase to be guessed (max 85 characters)"
        ),
    ):

        await game.lock.acquire()

        if game.status != "Inactive":
            await interaction.send("A game is already running.", ephemeral=True)

        else:
            if len(phrase) > 85:
                await interaction.send(
                    "Phrase is too long, please try again", ephemeral=True
                )
                return

            await interaction.send(
                "Phrase accepted - game is starting!", ephemeral=True
            )
            await interaction.channel.send("Void Hangman has begun!")
            game.setup(
                phrase,
                interaction.user,
                interaction.channel,
            )
            await interaction.channel.send(embed=game.embed)
            game.lock.release()

    @hangman.subcommand(description="Attempt a guess")
    async def guess(
        self,
        interaction: Interaction,
        guess=SlashOption(
            description="Your guess - either a letter or the whole word/phrase"
        ),
    ):

        global game

        if game.status == "Inactive":
            await interaction.send("No active game found.", ephemeral=True)
        elif game.channel != interaction.channel:
            await interaction.send(
                f"You can only make guesses in the current game's channel, please head over to {game.channel.mention}.",
                ephemeral=True,
            )
        elif game.host == interaction.user:
            await interaction.send("Hey, no cheating!", ephemeral=True)
        else:

            guess = guess.upper()

            if guess in game.progress or guess in game.wrong_guesses:
                await interaction.send(f"{guess} has already been guessed!")
                return

            if len(guess) == 1:
                if game.check_letter(guess):
                    await interaction.send(f"Ding ding ding - {guess} is a hit!")
                else:
                    await interaction.send(f"Sorry, no {guess}.")

            elif len(guess) == len(game.word):
                if not game.check_word(guess):
                    await interaction.send(f"{guess} isn't correct, sorry.")
            else:
                await interaction.send(
                    "You can only guess single letters or the entire word/phrase.",
                    ephemeral=True,
                )
                return

            if game.state() == "Game Over":
                await interaction.send(
                    "Game Over - better luck next time!", embed=game.embed
                )
                game = HangmanGame()
            elif game.state() == "Game Won":
                await interaction.send(
                    "Winner winner chicken dinner!", embed=game.embed
                )
                game = HangmanGame()
            else:
                await interaction.channel.send(embed=game.embed)

    @hangman.subcommand(description="Abort the current game of Void Hangman")
    async def abort(self, interaction: Interaction):
        global game

        if game.status != "Active":
            await interaction.send("No active game found.", ephemeral=True)
        elif (
            interaction.user != game.host
            or get_role(interaction.guild, "Moderator") not in interaction.user.roles
        ):
            await interaction.send(
                "Only the person who started the game can stop it.", ephemeral=True
            )
        else:
            await interaction.send("Game aborted. Use `/hangman` to start a new one.")
            game = HangmanGame()


def setup(bot):
    bot.add_cog(Hangman(bot))
