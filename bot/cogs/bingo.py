import asyncio
import random

from nextcord import SlashOption, slash_command
from nextcord.ext.commands import Cog

from utils import util_functions as uf


class BingoCard:
    def __init__(self):
        self.grid = [random.sample(range(i, i + 15), 5) for i in range(1, 76, 15)]
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
                if type(self.grid[coords[0]][coords[1]]) is int:
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
        self.draws = []


    def setup(self, host, channel):
        self.status = "Lobby open"
        self.host = host
        self.channel = channel


    async def draw(self):
        if len(self.draws) == 0:
            await self.channel.send("All numbers have been drawn - please check your cards.")
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
            await self.channel.send("Check your cards one last time - the game will finish in 30 seconds.")
            await asyncio.sleep(15)
            await self.channel.send("15 seconds remaining.")
            await asyncio.sleep(15)
            await self.channel.send("The game has finished!")
            if len(self.winners) == 1:
                await self.channel.send(f"The winner is {self.winners[0]}.")
            else:
                await self.channel.send(f"The winners are {', '.join(self.winners[:-1])} and {self.winners[-1]}")
        else:
            self.winners.append(winner.mention)
            self.lock.release()


game = BingoGame()


class Bingo(Cog, name="Void Bingo", description="Embrace your inner boomer and play some Void Bingo - win by "
                                                "completing a row, column or diagonal (middle square is free)."):
    def __init__(self, bot):
        self.bot = bot


    async def create(self, interaction):
        if game.status == "Lobby open":
            await interaction.send("A lobby is already open, use `/bingo` to join.", ephemeral=True)
        elif game.status == "Active":
            await interaction.send("A game is already running, please wait for the next one.", ephemeral=True)
        else:
            game.setup(host=interaction.user, channel=interaction.channel)
            await interaction.send("Lobby created, use `/bingo` to join.")


    async def join(self, interaction):
        if game.status == "Inactive":
            await interaction.send("No open lobby found - use `/bingo` to create one.", ephemeral=True)
        elif game.status == "Active":
            await interaction.send("A game is already running, please wait for the next one.", ephemeral=True)
        elif game.channel != interaction.channel:
            await interaction.send(f"Please head over to {game.channel.mention} to join the current lobby.",
                                   ephemeral=True)
        elif interaction.user in game.players:
            await interaction.send("You're already in this lobby.", ephemeral=True)
        else:
            game.players.append(interaction.user)
            await interaction.send(f"Welcome {interaction.user.display_name}. Players currently in "
                                   f"lobby: {len(game.players)}. The game host can use `/bingo` to start the game.")


    async def start(self, interaction):
        if game.status == "Inactive":
            await interaction.send("No open lobby found - use `/bingo` to create one.", ephemeral=True)
        elif game.status == "Active":
            await interaction.send("A game is already running, please wait for the next one.", ephemeral=True)
        elif game.host != interaction.user and (
                uf.get_role(interaction.guild, "Moderator") not in interaction.user.roles) and (
                uf.get_role(interaction.guild, "Guides of the Void") not in interaction.user.roles):
            await interaction.send("Only the person who created the lobby can start the game.", ephemeral=True)
        elif game.channel != interaction.channel:
            await interaction.send(f"Please head over to {game.channel.mention} to start the game.", ephemeral=True)
        elif len(game.players) == 0:
            await interaction.send("The lobby is empty, use `/bingo` to join.")
        else:
            await game.start()
            await interaction.send("Void Bingo has begun! Type use `/bingo` to draw a number (or toggle the autodraw).")


async def stop(self, interaction):
    global game

    if game.status != "Active":
        await interaction.send("No active game found.", ephemeral=True)
    elif game.host != interaction.user and (
            uf.get_role(interaction.guild, "Moderator") not in interaction.user.roles) and (
            uf.get_role(interaction.guild, "Guides of the Void") not in interaction.user.roles):
        await interaction.send("Only the person who started the game can stop it.", ephemeral=True)
    elif len(game.winners) > 0:
        await interaction.send("One or more players have Void Bingo - the game will automatically finish soon.",
                               ephemeral=True)
    else:
        game = BingoGame()
        await interaction.send("Game stopped. Use `/bingo` to start a new one")


async def draw(self, interaction):
    if game.status != "Active":
        await interaction.send("No active game found.", ephemeral=True)
    elif interaction.user != game.host and (
            uf.get_role(interaction.guild, "Moderator") not in interaction.user.roles) and (
            uf.get_role(interaction.guild, "Guides of the Void") not in interaction.user.roles):
        await interaction.send("Only the person who started the game can draw numbers.", ephemeral=True)
    elif game.channel != interaction.channel:
        await interaction.send(f"Numbers may only be drawn in the current game's channel, "
                               f"please head over to {game.channel.mention}.", ephemeral=True)
    elif len(game.winners) > 0:
        await interaction.send("One or more players have Bingo, no more numbers may be drawn.", ephemeral=True)
    elif len(game.draws) == 0:
        await interaction.send("All numbers have already been drawn - please check your cards.")
    else:
        await game.draw()


async def autodraw(self, interaction):
    if game.status != "Active":
        await interaction.send("No active game found.", ephemeral=True)
    elif interaction.user != game.host and (
            uf.get_role(interaction.guild, "Moderator") not in interaction.user.roles) and (
            uf.get_role(interaction.guild, "Guides of the Void") not in interaction.user.roles):
        await interaction.send("Only the person who started the game can draw numbers.", ephemeral=True)
    elif game.channel != interaction.channel:
        await interaction.send(f"Numbers may only be drawn in the current game's channel, "
                               f"please head over to {game.channel.mention}.", ephemeral=True)
    elif len(game.winners) > 0:
        await interaction.send("One or more players have Bingo, no more numbers may be drawn.", ephemeral=True)
    elif len(game.draws) == 0:
        await interaction.send("All numbers have already been drawn - please check your cards.")
    else:
        game.autodraw = not game.autodraw
        if game.autodraw:
            await interaction.send("Automatic drawing started.")
        else:
            await interaction.send("Automatic drawing stopped.")
        while game.autodraw:
            await game.draw()
            await asyncio.sleep(15)


async def declare(self, interaction):
    global game

    if game.status != "Active" or interaction.user not in game.players:
        await interaction.send("You are not currently in a game.", ephemeral=True)
    elif not game.cards[interaction.user].check():
        await interaction.send("You don't have Void Bingo - check your card again.", ephemeral=True)
    elif interaction.user.mention in game.winners:
        await interaction.send("You have already declared Void Bingo.", ephemeral=True)
    else:
        await interaction.send("VOID BINGO!")
        await game.bingo(winner=interaction.user)
        game = BingoGame()


@slash_command(description="Play Void Bingo")
async def bingo(self, interaction, action: str = SlashOption(choices={
    "Create a lobby": "create",
    "Join the lobby": "join",
    "Start the game": "start",
    "Stop the game": "stop",
    "Draw a number": "draw",
    "Toggle autodraw": "autodraw",
    "Declare Void Bingo!": "declare"
}, description="Choose the action you want to take", name="action")):
    cmd_dict = {
        "create": self.create,
        "join": self.join,
        "start": self.start,
        "stop": self.stop,
        "draw": self.draw,
        "autodraw": self.autodraw,
        "declare": self.declare,
    }
    cmd = cmd_dict[action]
    await cmd(interaction)


def setup(bot):
    bot.add_cog(Bingo(bot))
