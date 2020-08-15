import random
import re
from discord.ext import commands


class Rando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="RPG format dice roller")
    async def roll(self, ctx, *args):
        args = "".join(args)
        rolls = re.split(r"\+", args)
        results = []
        if re.search(r"^\d+d\d+(\+\d+d\d+)*$", args) is None:
            raise commands.errors.BadArgument(message="Improper dice format")
        else:
            output = "Rolling " + re.sub(r"\+", r" \+ ", args) + " = "
            for roll in rolls:
                num, die = [int(x) for x in re.split("d", roll)]
                res = [random.randint(1, die) for i in range(num)]
                results.append(res)
            total = sum([sum(res) for res in results])
            output += str(total) + "\nRolls: "
            output += str(results)[1:-1]
            output = re.sub(r"\[", "(", output)
            output = re.sub(r"\]", ")", output)
            output = re.sub(r"\),", ") +", output)
            await ctx.send(output)

    @commands.command(brief="Gives a random number between 1 and 6")
    async def dice(self, ctx):
        await ctx.send(random.randrange(1, 7))

    @commands.command(brief="Gives randomly heads or tails")
    async def coin(self, ctx):
        n = random.randint(0, 1)
        await ctx.send("Heads" if n == 1 else "Tails")


def setup(bot):
    bot.add_cog(Rando(bot))
