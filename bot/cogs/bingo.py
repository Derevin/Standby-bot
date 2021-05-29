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


game = BingoGame()


class Bingo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bcreate(self, ctx):
        global game
        if game.status == "Lobby open":
            await ctx.send("A lobby is already open, type `+bjoin` to join.")
        elif game.status == "Active":
            await ctx.send("A game is already running, please wait for the next one.")
        else:
            game.status = "Lobby open"
            game.host = ctx.author
            game.channel = ctx.channel
            await ctx.send("Lobby created, type `+bjoin` to join.")

    @commands.command()
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
        else:
            game.players.append(ctx.author)
            await ctx.send(
                f"Welcome {ctx.author.display_name}. Players currently in lobby: {len(game.players)}."
            )

    @commands.command()
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
            for player in game.players:
                game.cards[player] = BingoCard()
                await player.send("Welcome to Void Bingo! Here is your card.")
                msg = await player.send(game.cards[player])
                game.messages[player] = msg
            game.status = "Active"
            game.draws = list(range(1, 76))
            random.shuffle(game.draws)
            await ctx.send("Void Bingo has begun! Type `+bdraw` to draw a number.")

    @commands.command()
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
                "One or more players have Bingo - the game will automatically finish soon."
            )
        else:
            game = BingoGame()
            await ctx.send("Game stopped. Type `+bcreate` to start a new one")

    @commands.command()
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
            num = game.draws.pop()
            await ctx.send(f"The number is {num}.")
            for player in game.players:
                result = game.cards[player].mark(num)
                if result == "Hit":
                    await player.send(f"{num} is a hit! Your card has been updated.")
                    await game.messages[player].edit(content=game.cards[player])

    @commands.command()
    async def bingo(self, ctx):
        global game
        if game.status != "Active" or ctx.author not in game.players:
            await ctx.send("You are not currently in a game.")
        elif not game.cards[ctx.author].check():
            await ctx.send(
                "You don't have bingo - check your card again.", reference=ctx.message,
            )
        elif ctx.author.mention in game.winners:
            await ctx.send("You have already declared Bingo.", reference=ctx.message)
        else:
            await ctx.send("BINGO!", reference=ctx.message)
            await game.lock.acquire()
            game.winners.append(ctx.author.mention)
            if len(game.winners) > 1:
                game.lock.release()
            else:
                game.lock.release()
                await ctx.send(
                    "Check your cards one last time - the game will finish in 30 seconds."
                )
                await asyncio.sleep(15)
                await ctx.send("15 seconds remaining.")
                await asyncio.sleep(15)
                await ctx.send("The game has finished!")
                if len(game.winners) == 1:
                    await ctx.send(f"The winner is {game.winners[0]}.")
                else:
                    await ctx.send(
                        f"The winners are {', '.join(game.winners[:-1])} and {game.winners[-1]}"
                    )
                game = BingoGame()


def setup(bot):
    bot.add_cog(Bingo(bot))
