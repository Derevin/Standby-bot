import asyncio
from discord.ext import commands
import random
from utils.util_functions import *


class BingoCard:
    def __init__(self):
        self.grid = [
            random.sample(range(1, 16), 5),
            random.sample(range(16, 31), 5),
            random.sample(range(31, 46), 5),
            random.sample(range(46, 61), 5),
            random.sample(range(61, 76), 5),
        ]
        self.grid[2][2] = "Free"

    def __str__(self):
        printout = "```\n" + 16 * "_" + "\n\n"
        for i in range(5):
            for j in range(5):
                if i == 2 or j != 2:
                    printout += str(self.grid[j][i]).zfill(2) + " "
                else:
                    printout += " " + str(self.grid[j][i]).zfill(2) + "  "
            printout += "\n" + 16 * "_" + "\n\n"
        printout += "```"
        return printout

    def mark(self, number):
        col = int((number - 1) / 15)
        if number in self.grid[col]:
            res = "Hit"
            self.grid[col][self.grid[col].index(number)] = " X"
        else:
            res = "Miss"
        return res

    def check(self):
        patterns = []
        for i in range(5):
            row = []
            col = []
            for j in range(5):
                col.append((i, j))
                row.append((j, i))
            patterns.append(row)
            patterns.append(col)
        diag1 = [(i, i) for i in range(5)]
        diag2 = [(i, 4 - i) for i in range(5)]
        patterns.append(diag1)
        patterns.append(diag2)

        for pattern in patterns:
            bingo = True
            for coords in pattern:
                if type(self.grid[coords[0]][coords[1]]) == int:
                    bingo = False
                    break
            if bingo:
                return True
        return False


class BingoGame:
    def __init__(self):
        self.status = "Inactive"
        self.players = []
        self.cards = {}
        self.messages = {}
        self.winners = []
        self.lock = asyncio.Lock()
        self.autodraw = False
        self.host = None
        self.channel = None

    def setup(self, host, channel):
        self.status = "Lobby open"
        self.host = host
        self.channel = channel

    async def draw(self):
        if len(self.draws) == 0:
            await self.channel.send(
                "All numbers have been drawn - please check your cards."
            )
            self.autodraw = False
        else:
            num = self.draws.pop()
            await self.channel.send(f"The number {num} has been drawn.")
            for player in self.players:
                result = self.cards[player].mark(num)
                if result == "Hit":
                    await player.send(f"{num} is a hit! Your card has been updated.")
                    await self.messages[player].edit(content=self.cards[player])

    async def start(self):
        for player in self.players:
            self.cards[player] = BingoCard()
            await player.send("Welcome to Void Bingo! Here is your card.")
            msg = await player.send(self.cards[player])
            self.messages[player] = msg
        self.status = "Active"
        self.draws = list(range(1, 76))
        random.shuffle(game.draws)

    async def bingo(self, winner):
        await self.lock.acquire()
        if len(self.winners) == 0:
            self.winners.append(winner.mention)
            self.lock.release()
            await self.channel.send(
                "Check your cards one last time - the game will finish in 30 seconds."
            )
            await asyncio.sleep(15)
            await self.channel.send("15 seconds remaining.")
            await asyncio.sleep(15)
            await self.channel.send("The game has finished!")
            if len(self.winners) == 1:
                await self.channel.send(f"The winner is {self.winners[0]}.")
            else:
                await self.channel.send(
                    f"The winners are {', '.join(self.winners[:-1])} and {self.winners[-1]}"
                )
        else:
            self.winners.append(winner.mention)
            self.lock.release()


game = BingoGame()


class Bingo(
    commands.Cog,
    name="Void Bingo",
    description="""Embrace your inner boomer and play some Void Bingo - win by completing """
    """a row, column or diagonal (middle square is free).""",
):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Creates a Void Bingo lobby.")
    async def bcreate(self, ctx):
        global game
        if game.status == "Lobby open":
            await ctx.send("A lobby is already open, type `+bjoin` to join.")
        elif game.status == "Active":
            await ctx.send("A game is already running, please wait for the next one.")
        else:
            game.setup(host=ctx.author, channel=ctx.channel)
            await ctx.send("Lobby created, type `+bjoin` to join.")

    @commands.command(brief="Joins an open Void Bingo lobby.")
    async def bjoin(self, ctx):
        global game
        if game.status == "Inactive":
            await ctx.send("No open lobby found - type `+bcreate` to create one.")
        elif game.status == "Active":
            await ctx.send("A game is already running, please wait for the next one.")
        elif game.channel != ctx.channel:
            await ctx.send(
                f"Please head over to {game.channel.mention} to join the current lobby."
            )
        elif ctx.author in game.players:
            await ctx.send("You're already in this lobby.")
        else:
            game.players.append(ctx.author)
            await ctx.send(
                f"""Welcome {ctx.author.display_name}. Players currently in lobby: {len(game.players)}. """
                """The game host can type `+bstart` to start the game."""
            )

    @commands.command(brief="Begins a game of Void Bingo with the current lobby.")
    async def bstart(self, ctx):
        global game
        if game.status == "Inactive":
            await ctx.send("No open lobby found - type `+bcreate` to create one.")
        elif game.status == "Active":
            await ctx.send("A game is already running, please wait for the next one.")
        elif (
            game.host != ctx.author
            and get_role(ctx.guild, "Moderator") not in ctx.author.roles
            and get_role(ctx.guild, "Guides of the Void") not in ctx.author.roles
        ):
            await ctx.send("Only the person who created the lobby can start the game.")
        elif game.channel != ctx.channel:
            await ctx.send(
                f"Please head over to {game.channel.mention} to start the game."
            )
        elif len(game.players) == 0:
            await ctx.send("The lobby is empty, type `+bjoin` to join.")
        else:
            await game.start()
            await ctx.send("Void Bingo has begun! Type `+bdraw` to draw a number.")

    @commands.command(brief="Aborts the current game of Void Bingo.")
    async def bstop(self, ctx):
        global game
        if game.status != "Active":
            await ctx.send("No active game found.")
        elif (
            game.host != ctx.author
            and get_role(ctx.guild, "Moderator") not in ctx.author.roles
            and get_role(ctx.guild, "Guides of the Void") not in ctx.author.roles
        ):
            await ctx.send("Only the person who started the game can stop it.")
        elif len(game.winners) > 0:
            await ctx.send(
                "One or more players have Void Bingo - the game will automatically finish soon."
            )
        else:
            game = BingoGame()
            await ctx.send("Game stopped. Type `+bcreate` to start a new one")

    @commands.command(brief="Draws a number.")
    async def bdraw(self, ctx):
        global game

        if game.status != "Active":
            await ctx.send("No active game found.")
        elif (
            ctx.author != game.host
            and get_role(ctx.guild, "Moderator") not in ctx.author.roles
            and get_role(ctx.guild, "Guides of the Void") not in ctx.author.roles
        ):
            await ctx.send("Only the person who started the game can draw numbers.")
        elif game.channel != ctx.channel:
            await ctx.send(
                f"Numbers may only be drawn in the current game's channel, please head over to {game.channel.mention}."
            )
        elif len(game.winners) > 0:
            await ctx.send(
                "One or more players have Bingo, no more numbers may be drawn."
            )
        elif len(game.draws) == 0:
            await ctx.send(
                "All numbers have already been drawn - please check your cards."
            )
        else:
            await game.draw()

    @commands.command(brief="Automatically draws numbers.")
    async def bautodraw(self, ctx):
        global game
        if game.status != "Active":
            await ctx.send("No active game found.")
        elif (
            ctx.author != game.host
            and get_role(ctx.guild, "Moderator") not in ctx.author.roles
            and get_role(ctx.guild, "Guides of the Void") not in ctx.author.roles
        ):
            await ctx.send("Only the person who started the game can draw numbers.")
        elif game.channel != ctx.channel:
            await ctx.send(
                f"Numbers may only be drawn in the current game's channel, please head over to {game.channel.mention}."
            )
        elif len(game.winners) > 0:
            await ctx.send(
                "One or more players have Bingo, no more numbers may be drawn."
            )
        elif len(game.draws) == 0:
            await ctx.send(
                "All numbers have already been drawn - please check your cards."
            )
        else:
            game.autodraw = not game.autodraw
            if game.autodraw:
                await ctx.send("Automatic drawing started.")
            else:
                await ctx.send("Automatic drawing stopped.")
            while game.autodraw:
                await game.draw()
                await asyncio.sleep(15)

    @commands.command(brief="Declare Void Bingo!")
    async def bingo(self, ctx):
        global game
        if game.status != "Active" or ctx.author not in game.players:
            await ctx.send("You are not currently in a game.")
        elif not game.cards[ctx.author].check():
            await ctx.send(
                "You don't have Void Bingo - check your card again.",
                reference=ctx.message,
            )
        elif ctx.author.mention in game.winners:
            await ctx.send(
                "You have already declared Void Bingo.", reference=ctx.message
            )
        else:
            await ctx.send("VOID BINGO!", reference=ctx.message)
            await game.bingo(winner=ctx.author)
            game = BingoGame()


def setup(bot):
    bot.add_cog(Bingo(bot))
