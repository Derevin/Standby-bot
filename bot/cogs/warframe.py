from discord.ext import commands
import discord
from settings import *
import settings_files.warframe_data as wf
from gekko import GEKKO
import numpy as np


class Warframe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Finds the highest DPS build for a weapon")
    async def build(self, ctx, *, weapon):
        # TODO: Toggle conditionals via input
        #       Add riven via input

        async with ctx.channel.typing():

            # Load weapon and mod data
            if weapon.lower() not in wf.arsenal:
                raise commands.errors.BadArgument(
                    "The weapon does not exist or has not yet been added."
                )

            weapon = wf.arsenal[weapon.lower()]
            modlist = wf.all_mods.get(weapon)

            # Initialize model
            m = GEKKO()

            # Initialize variables
            n = len(modlist)
            x = m.Array(m.Var, n, value=0, lb=0, ub=1, integer=True)

            matrix = np.array(modlist.matrix()).T
            bonuses = matrix @ x

            # Get special indices
            ser = modlist.index("Serration")
            cal = modlist.index("Heavy Caliber")
            ele = modlist.element_indices()
            vig = modlist.vigilante_indices()
            con = modlist.conditional_indices()

            # Construct multipliers
            damage = 1 + bonuses[0]
            multishot = 1 + bonuses[1]
            cc = weapon.cc * (1 + bonuses[2])
            cd = weapon.cd * (1 + bonuses[3])
            critical = 1 + cc * (cd - 1) * (1 + 0.05 * m.sum(x[vig]))
            elemental = (
                1
                + bonuses[4]
                + bonuses[5] * weapon.ips()[0]
                + bonuses[6] * weapon.ips()[1]
                + bonuses[7] * weapon.ips()[2]
            )
            fire_rate = weapon.fire_rate * (1 + bonuses[8])
            mag = weapon.mag * (1 + bonuses[9])
            rel = weapon.reload / (1 + bonuses[10])
            rate = mag / (mag / fire_rate + rel)

            # Set conditions
            m.Equation(m.sum(x) <= 8)  # 8 Mod Capacity

            m.Equation(m.sum(x[ele]) > 2)  # Use at least 2 elemental mods

            if weapon.compat not in ["SHOTGUN", "PISTOL"]:
                m.Equation(x[ser] >= x[cal])  # Use Serration before Heavy Caliber

            use_conditionals = False
            if not use_conditionals:
                m.Equation(m.sum(x[con]) == 0)

            # Set objective
            m.Obj(((-1) * damage * multishot * critical * elemental * rate))

            # Set solver to integer programming
            m.options.SOLVER = 1
            # Optimize
            m.solve(disp=False)

            # Results
            config = wf.Modlist()
            config.mods = [modlist[i] for i in range(n) if str(x[i].value) == "[1.0]"]
            config.mods.sort(reverse=True)
            await ctx.send(config.names())
            await ctx.send(
                "Disclaimer - this is very much a WIP. If it looks wrong, it probably is."
            )


def setup(bot):
    bot.add_cog(Warframe(bot))
