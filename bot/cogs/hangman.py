import asyncio
from discord.ext import commands
import discord
import re
import random
from settings import *
from utils.util_functions import *

image_links = [
    "https://upload.wikimedia.org/wikipedia/commons/8/8b/Hangman-0.png",
    "https://upload.wikimedia.org/wikipedia/commons/3/30/Hangman-1.png",
    "https://upload.wikimedia.org/wikipedia/commons/7/70/Hangman-2.png",
    "https://upload.wikimedia.org/wikipedia/commons/9/97/Hangman-3.png",
    "https://upload.wikimedia.org/wikipedia/commons/2/27/Hangman-4.png",
    "https://upload.wikimedia.org/wikipedia/commons/6/6b/Hangman-5.png",
    "https://upload.wikimedia.org/wikipedia/commons/d/d6/Hangman-6.png",
]


class HangmanGame:
    def __init__(self):
        self.status = "Inactive"
        self.lock = asyncio.Lock()

    def create_embed(self):

        embed = discord.Embed(color=PALE_GREEN)
        title = re.sub(" ", "   ", self.progress)
        title = re.sub("_", r"\_ ", title)
        title = re.sub(r"(\w)", r"\1 ", title)
        embed.title = title if len(self.wrong_guesses) < 6 else self.word
        if len(self.wrong_guesses) >= 6:
            desc = "Game over! Type `+hangman` to start another round."
        elif self.word == self.progress:
            desc = "Game won! Type `+hangman` to start another round."
        else:
            desc = "Welcome to Void Hangman! Use `+guess` to guess a letter or the whole word/phrase."
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

    @commands.command(brief="Start a game of Void Hangman")
    async def hangman(self, ctx):

        await game.lock.acquire()
        if game.status != "Inactive":
            await ctx.send("A game is already running.")
        else:
            game.status = "Choosing word"
            game.lock.release()
            await ctx.send(
                f"Void Hangman has begun! {ctx.author.mention} is currently choosing a word."
            )
            await ctx.author.send(
                """You have started a round of Void Hangman! """
                """Please reply to me here with the word or phrase you want people to guess (max 85 characters)."""
            )
            try:

                def check(m):
                    return (
                        type(m.channel) == discord.channel.DMChannel
                        and m.channel.recipient == ctx.author
                        and len(m.content) < 86
                    )

                msg = await self.bot.wait_for("message", timeout=90, check=check)

            except asyncio.TimeoutError:
                await ctx.send(
                    f"{ctx.author.mention} took too long to choose a word - game aborted."
                )
                game.status = "Inactive"
            else:
                game.setup(
                    msg.content,
                    ctx.author,
                    ctx.channel,
                )
                await ctx.send(embed=game.embed)

    @commands.command(brief="Attempt a guess")
    async def guess(self, ctx, *, guess):

        global game

        if game.status == "Inactive":
            await ctx.send("No active game found.")
        elif game.status == "Choosing word":
            await ctx.send(f"{game.host.mention} is choosing the word - please wait.")
        elif game.channel != ctx.channel:
            await ctx.send(
                f"You can only make guesses in the current game's channel, please head over to {game.channel.mention}."
            )
        elif game.host == ctx.author:
            await ctx.send("Hey, no cheating.")
        else:

            guess = guess.upper()
            if guess in game.progress or guess in game.wrong_guesses:
                await ctx.send(f"{guess} has already been guessed!")
                return

            if len(guess) == 1:
                if game.check_letter(guess):
                    await ctx.send("Ding ding ding!")
                else:
                    await ctx.send(f"Sorry, no {guess}.")

            elif len(guess) == len(game.word):
                if not game.check_word(guess):
                    await ctx.send("That's not it, sorry.")
            else:
                await ctx.send(
                    "You can only guess single letters or the entire word/phrase."
                )
                return

            if game.state() == "Game Over":
                await ctx.send("Game Over - better luck next time!", embed=game.embed)
                game = HangmanGame()
            elif game.state() == "Game Won":
                await ctx.send("Winner winner chicken dinner!", embed=game.embed)
                game = HangmanGame()
            else:
                await ctx.send(embed=game.embed)

    @commands.command(brief="Abort the current game of Void Hangman")
    async def hstop(self, ctx):
        global game
        if game.status != "Active":
            await ctx.send("No active game found.")
        elif (
            ctx.author != game.host
            or get_role(ctx.guild, "Moderator") not in ctx.author.roles
        ):
            await ctx.send("Only the person who started the game can stop it.")
        else:
            await ctx.send("Game aborted, type `+hangman` to start a new one.")
            game = HangmanGame()


def setup(bot):
    bot.add_cog(Hangman(bot))
