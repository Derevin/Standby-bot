from discord.ext import commands
import discord
from settings import *
import settings_files.warframe_data as wf
from gekko import GEKKO
import numpy as np
import re


class Warframe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Finds the highest DPS build for a weapon")
    async def build(self, ctx, weapon, riven=None, *reqs):

        async with ctx.channel.typing():

            # Load weapon and mod data

            args = [weapon]  # This is ugly but I want the +help text to look right
            if riven is not None:
                args = [weapon, riven]
                args.extend(reqs)

            weapon_name = "none"
            index = 6
            while weapon_name not in wf.arsenal and index != 0:
                index -= 1
                weapon_name = " ".join(args[:index]).lower()

            try:
                weapon = wf.arsenal[weapon_name]
            except KeyError:
                raise commands.errors.BadArgument(
                    "The weapon does not exist or has not yet been added."
                )
            modlist = wf.dps_mods.get(weapon)

            args = args[index:]  # Remove weapon name
            arg_text = " ".join(args).title()
            args = re.split("(?<!%)(?<!Fire) ", arg_text)  # Split into stats

            riven = wf.Mod("Riven")
            reqs = []

            for item in args:
                stat, amount, _ = wf.parse_stats(item)
                if stat is not None:
                    riven.increase(stat, amount)
                else:
                    reqs.append(item)

            if riven.has_dps_stats():
                modlist.add(riven)

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
            mgn = modlist.index("Magnum Force")
            ele = modlist.index("Elements")
            vig = modlist.index("Vigilante")
            con = modlist.index("Conditionals")
            stc = modlist.index("Status")
            phy = modlist.index("Physical")

            # Construct multipliers
            damage = 1 + bonuses[0]
            multishot = 1 + bonuses[1]
            cc = weapon.cc * (1 + bonuses[2])
            cd = weapon.cd * (1 + bonuses[3])
            critical = 1 + cc * (cd - 1) * (1 + 0.05 * m.sum(x[vig]))
            elemental = (
                1
                + bonuses[4]
                + bonuses[9] * weapon.ips()[0]
                + bonuses[10] * weapon.ips()[1]
                + bonuses[11] * weapon.ips()[2]
            )
            fire_rate = weapon.fire_rate * (1 + bonuses[6])
            rel = weapon.reload / (1 + bonuses[7])
            mag = weapon.mag * (1 + bonuses[8])
            rate = mag / (mag / fire_rate + rel)

            # Create special requirements
            reqs = " ".join(reqs)

            use_conditionals = re.search("conditional", reqs, re.I) is not None
            no_heavy_cal = re.search("no heavy cal(iber)?", reqs, re.I) is not None
            no_magnum = re.search("no magnum( force)?", reqs, re.I) is not None
            use_ips = re.search("ips ok", reqs, re.I) is not None
            use_status = re.search(r"(\d) status", reqs, re.I)
            min_elements = re.search(r"(\d) elements", reqs, re.I)

            # Set conditions (Don't use strict inequalities)
            m.Equation(m.sum(x) <= 8)  # 8 Mod Capacity

            if not use_conditionals:
                m.Equation(m.sum(x[con]) == 0)

            if not use_ips:
                m.Equation(m.sum(x[phy]) == 0)

            if use_status:
                m.Equation(m.sum(x[stc]) == int(use_status.group(1)))

            if min_elements:
                m.Equation(m.sum(x[ele]) == int(min_elements.group(1)))

            # Weapon class specific conditions
            if weapon.compat == "PISTOL":

                if no_magnum:
                    m.Equation(x[mgn] == 0)

            elif weapon.compat == "SHOTGUN":
                pass

            else:  # Rifle

                m.Equation(x[ser] >= x[cal])  # Use Serration before Heavy Caliber

                if no_heavy_cal:
                    m.Equation(x[cal] == 0)

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
            await ctx.send(f"Final multiplier: {int(-m.options.OBJFCNVAL)}")
            await ctx.send(
                "Disclaimer - this is very much a WIP. If it looks wrong, it probably is."
            )


def setup(bot):
    bot.add_cog(Warframe(bot))
