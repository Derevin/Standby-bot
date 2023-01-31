import random
import re

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from settings import *


class Rando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="RNG commands", name="rng")
    async def rng(self, interaction):
        pass

    @rng.subcommand(description="RPG format dice roller")
    async def roll(
        self,
        interaction: Interaction,
        dice_roll=SlashOption(description="Your dice roll"),
    ):
        dice = re.sub(" ", "", dice_roll)
        rolls = re.split(r"\+", dice)
        results = []
        bonus = []
        if re.search(r"^(\d*d\d+|\d+)(\+(\d*d\d+|\d+))*$", dice) is None:
            raise commands.errors.BadArgument(message="Improper dice format")
        else:
            output = "Rolling " + re.sub(r"\+", r" \+ ", dice) + " = "
            for roll in rolls:
                if re.search(r"^\d+$", roll):
                    bonus.append(int(roll))
                else:
                    if re.search("^d", roll):
                        roll = "1" + roll
                    num, die = [int(x) for x in re.split("d", roll)]
                    res = [random.randint(1, die) for i in range(num)]
                    results.append(res)
            total = sum([sum(res) for res in results]) + sum(bonus)
            output += str(total) + "\nRolls: "
            output += str(results)[1:-1]
            output = re.sub(r"\[", "(", output)
            output = re.sub(r"\]", ")", output)
            output = re.sub(r"\),", ") +", output)
            await interaction.send(output)

    @rng.subcommand(description="Rolls a regular six-sided die")
    async def dice(self, interaction: Interaction):
        await interaction.send(random.randrange(1, 7))

    @rng.subcommand(description="Flip a coin")
    async def coin(self, interaction: Interaction):
        n = random.randint(0, 1)
        await interaction.send("Heads" if n == 1 else "Tails")

    @rng.subcommand(description="Chooses from among the given options")
    async def choose(
        self,
        interaction: Interaction,
        choices=SlashOption(
            name="options",
            description="The options to choose from (separate with commas)",
        ),
    ):

        options = re.split(", ?", choices)
        if len(options) == 1:
            await interaction.send(
                f"Such a tough decision. I guess I'll have to go with {options[0]}"
            )
        else:
            print(options)
            choice = random.choice(options)
            phrases = [
                f"Let's go with {choice}",
                f"I choose {choice}",
                f"God has spoken to me - it must be {choice}",
                f"I have consulted with the spirits and they said {choice}",
                f"{choice} - no doubt about it",
                f"{choice} all day long",
                f"Obviously {choice}",
                f"9 out of 10 dentists recommend {choice}",
            ]
            await interaction.send(random.choice(phrases))

    @rng.subcommand(description="Roll 4d6 drop lowest and repeat 6 times")
    async def array(
        self,
        interaction: Interaction,
    ):

        message = "Rolling 4d6 drop lowest:"
        final_array = []

        for i in range(6):
            res = [random.randint(1, 6) for i in range(4)]
            m = str(min(res))
            final_array.append(sum(res) - min(res))
            formatted = "(" + re.sub(m, "~~" + m + "~~", str(res), 1)[1:-1] + ")"
            message += f"\nRoll {i+1}:\t{formatted} = {final_array[-1]}"

        final_array = map(str, final_array)
        message += (
            "\nFinal array: (" + ", ".join(list(reversed(sorted(final_array)))) + ")"
        )

        await interaction.send(message)


def setup(bot):
    bot.add_cog(Rando(bot))
