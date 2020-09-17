import random
import re
from discord.ext import commands


class Rando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="RPG format dice roller")
    async def roll(self, ctx, *args):
        dice = "".join(args)
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
            await ctx.send(output)

    @commands.command(brief="Rolls a regular six-sided die")
    async def dice(self, ctx):
        await ctx.send(random.randrange(1, 7))

    @commands.command(aliases=["flip", "coinflip"], brief="Flips a coin")
    async def coin(self, ctx):
        n = random.randint(0, 1)
        await ctx.send("Heads" if n == 1 else "Tails")

    @commands.command(aliases=["pick"], brief="Chooses from among the given options")
    async def choose(self, ctx, *args):
        if not args:
            raise commands.errors.MissingRequiredArgument(
                "Please enter at least one option"
            )
        options = re.split(", ?", " ".join(args))
        if len(options) == 1:
            await ctx.send(
                f"Such a tough decision. I guess I'll have to go with {options[0]}"
            )
        else:
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
            await ctx.send(random.choice(phrases))


def setup(bot):
    bot.add_cog(Rando(bot))
