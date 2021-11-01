from discord.ext import commands
import discord
import random
from utils.util_functions import *
from settings import *
from fuzzywuzzy import process
from transliterate import translit
from transliterate.base import TranslitLanguagePack, registry
from PIL import Image, ImageDraw, ImageFont
import requests
import io
from pathlib import Path

TOUCAN_PRAISE = """
░░░░░░░░▄▄▄▀▀▀▄▄███▄░░░░░░░░░░░░░░
░░░░░▄▀▀░░░░░░░▐░▀██▌░░░░░░░░░░░░░
░░░▄▀░░░░▄▄███░▌▀▀░▀█░░░░░░░░░░░░░
░░▄█░░▄▀▀▒▒▒▒▒▄▐░░░░█▌░░░░░░░░░░░░
░▐█▀▄▀▄▄▄▄▀▀▀▀▌░░░░░▐█▄░░░░░░░░░░░
░▌▄▄▀▀░░░░░░░░▌░░░░▄███████▄░░░░░░
░░░░░░░░░░░░░▐░░░░▐███████████▄░░░
░░░░░le░░░░░░░▐░░░░▐█████████████▄
░░░░toucan░░░░░░▀▄░░░▐█████████████▄
░░░░░░has░░░░░░░░▀▄▄███████████████
░░░░░arrived░░░░░░░░░░░░█▀██████░░
"""

YEEE = """
░░░░░░░░░░░░░░░░░░░░░░░░░░░
░░░░░░░░░░░░░▄███▄▄▄░░░░░░░
░░░░░░░░░▄▄▄██▀▀▀▀███▄░░░░░
░░░░░░░▄▀▀░░░░░░░░░░░▀█░░░░
░░░░▄▄▀░░░░░░░░░░░░░░░▀█░░░
░░░█░░░░░▀▄░░▄▀░░░░░░░░█░░░
░░░▐██▄░░▀▄▀▀▄▀░░▄██▀░▐▌░░░
░░░█▀█░▀░░░▀▀░░░▀░█▀░░▐▌░░░
░░░█░░▀▐░░░░░░░░▌▀░░░░░█░░░
░░░█░░░░░░░░░░░░░░░░░░░█░░░
░░░░█░░▀▄░░░░▄▀░░░░░░░░█░░░
░░░░█░░░░░░░░░░░▄▄░░░░█░░░░
░░░░░█▀██▀▀▀▀██▀░░░░░░█░░░░
░░░░░█░░▀████▀░░░░░░░█░░░░░
░░░░░░█░░░░░░░░░░░░▄█░░░░░░
░░░░░░░██░░░░░█▄▄▀▀░█░░░░░░
░░░░░░░░▀▀█▀▀▀▀░░░░░░█░░░░░
░░░░░░░░░█░░░░░░░░░░░░█░░░░
"""


memes = {
    "Invest": "https://cdn.discordapp.com/attachments/744224801429782679/799296186019741696/Invest_Button_Banner.png",
    "Chad yes": "https://cdn.discordapp.com/attachments/744224801429782679/799296476835610674/cover5.png",
    "Pointing Spiderman": (
        "https://cdn.discordapp.com/attachments/744224801429782679/799298056373534800/C-658VsXoAo3ovC.png"
    ),
    "Always has been": (
        "https://cdn.discordapp.com/attachments/744224801429782679/802392943620915220/Always-Has-Been.png"
    ),
    "Stonks": (
        "https://cdn.discordapp.com/attachments/744224801429782679/802547348940521492/Screen_Shot_2019-06-05_at_1.png"
    ),
    "Noted": "https://cdn.discordapp.com/attachments/744224801429782679/802549793913176074/kowalskicover.png",
    "Big brain temple tap": (
        "https://cdn.discordapp.com/attachments/744224801429782679/803778693624365066/highresrollsafe.png"
    ),
    "Spongebob aight imma head out": (
        "https://cdn.discordapp.com/attachments/744224801429782679/803779170176991272/spongebob.png"
    ),
    "I am the senate": "https://cdn.discordapp.com/attachments/744224801429782679/803780347627044914/87d.png",
    "DD stress cat": "https://cdn.discordapp.com/attachments/744224801429782679/803781720700485672/3mdb6pdclcr51.png",
    "Understandable, have a great day": (
        "https://cdn.discordapp.com/attachments/744224801429782679/828058522499416074/unknown.png"
    ),
    "You have no power here": "https://cdn.discordapp.com/attachments/744224801429782679/805832792004755486/keiyb.png",
    "Well yes but actually no": (
        "https://cdn.discordapp.com/attachments/744224801429782679/810929401322668062/unknown.png"
    ),
    "Unsee juice": "https://cdn.discordapp.com/attachments/744224801429782679/813170790971211786/df0.png",
    "oof": "https://cdn.discordapp.com/attachments/744224801429782679/825175112420032562/unknown.png",
    "Epic embed fail": [
        "https://cdn.discordapp.com/attachments/744224801429782679/826115081027846144/embed.gif",
        "https://cdn.discordapp.com/attachments/744224801429782679/829356227171581992/image0-4.png",
    ],
    "Pathetic": "https://cdn.discordapp.com/attachments/744224801429782679/826798511793373254/1t5np8.png",
    "oh lmao rip": "https://cdn.discordapp.com/attachments/744224801429782679/827236052062175322/image0.png",
    "I love democracy": "https://cdn.discordapp.com/attachments/744224801429782679/827236877328318474/palp.png",
    "Shame (Mordor)": "https://cdn.discordapp.com/attachments/744224801429782679/838151854327463936/rwye5emkqe301.png",
    "Shame (Hot Fuzz)": "https://tenor.com/view/shame-pity-reload-shotgun-gif-5160379",
    "Same": "https://cdn.discordapp.com/attachments/744224801429782679/838169939784499230/r45ahkjo0ih41.png",
    "Steve Buscemi": "https://cdn.discordapp.com/attachments/744224801429782679/838170137659834378/steve.png",
    "False Shepherd Mark Edited": (
        "https://cdn.discordapp.com/attachments/744224801429782679/845726754408497182/unknown.png"
    ),
    "Don't give me hope": "https://cdn.discordapp.com/attachments/744224801429782679/846529020266151977/5aszwj.png",
    "Perfection": "https://cdn.discordapp.com/attachments/744224801429782679/846529089723957258/704.png",
    "Mod abuse": "https://cdn.discordapp.com/attachments/744224801429782679/851077716274053120/unknown.png",
    "Ironic": "https://cdn.discordapp.com/attachments/744224801429782679/851456678759104552/q9khzibd1x911.png",
    "I'm in this photo and I don't like it": (
        "https://cdn.discordapp.com/attachments/744224801429782679/851915990601433128/7a9.png"
    ),
    "Praise - le toucan has arrived": (
        "https://cdn.discordapp.com/attachments/743071403447943269/756976939591270431/unknown.png"
    ),
    "Horny": [
        "https://cdn.discordapp.com/attachments/620408411393228809/724613520318267422/ubil7fxr99551.png",
        "https://cdn.discordapp.com/attachments/267554564838785024/667115013412225054/image0.jpg",
        "https://i.kym-cdn.com/entries/icons/original/000/033/758/Screen_Shot_2020-04-28_at_12.21.48_PM.png",
        "https://cdn.discordapp.com/attachments/267554564838785024/701271178790305852/horny.jpg",
        "https://cdn.discordapp.com/attachments/267554564838785024/708425147064909944/x3x53kej4jr31.png",
        "https://cdn.discordapp.com/attachments/258941607238172673/717436181901475990/anti_horny.jpg",
        "https://cdn.discordapp.com/attachments/413861431906402334/"
        "810260242494783488/149741269_3647325365384706_5138601859788440225_n.png",
        "https://cdn.discordapp.com/attachments/744224801429782679/858313203402407936/E4s5y3gVUAIaSBX.png",
    ],
    "anime": "https://cdn.discordapp.com/attachments/744224801429782679/758417628544106546/4fmrlk.png",
    "cringe": "https://cdn.discordapp.com/attachments/441286267548729345/709160523907989524/EVACI9dUcAQp2Mb.png",
    "farquaad pointing": "https://cdn.discordapp.com/attachments/744224801429782679/897539202441433129/unknown.png",
}

meme_names = "\n".join(sorted(list(memes.keys()), key=str.casefold))
help_text = f"""
Currently available memes:\n{meme_names}
"""


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="YEE")
    async def yeeraw(self, ctx):
        await ctx.channel.send(YEEE)

    @commands.command(
        brief="YEE screenshot",
        aliases=[
            "yeee",
            "yeeee",
            "yeeeee",
            "yeeeeee",
            "yeeeeeee",
            "yeeeeeeee",
            "yeepic",
        ],
    )
    async def yee(self, ctx):
        await ctx.channel.send(
            "https://cdn.discordapp.com/attachments/738109782300557395/847974632551481384/unknown.png"
        )

    @commands.command(brief="Gives a user a hug")
    async def hug(self, ctx, *user):
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif ctx.message.reference:
            msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            user = msg.author
        else:
            user = get_user(ctx.guild, " ".join(user))

        if user:
            if user == ctx.author:
                await ctx.send(
                    "https://cdn.discordapp.com/attachments/744224801429782679/757549246533599292/selfhug.png"
                )
            else:
                await ctx.channel.send(
                    f"{user.mention}, {ctx.author.mention} sent you a hug!"
                )
                hug = get_emoji(ctx.guild, "BlobReachAndHug")
                if hug:
                    await ctx.channel.send(hug)

            await ctx.message.delete()

    @commands.command(brief="Pay your respects")
    async def f(self, ctx, *target):
        embed = discord.Embed()
        embed.description = (
            f"**{ctx.author.name}** has paid their respects"
            + (f" to **{' '.join(target)}**" if target else "")
            + "."
        )
        rip = await ctx.channel.send(embed=embed)
        await rip.add_reaction("🇫")

    @commands.command(brief="Posts a meme", aliases=["memed"], help=help_text)
    async def meme(self, ctx, *, query):

        cmd = re.split(" ", ctx.message.content)[0][1:]
        if cmd == "memed":
            await ctx.message.delete()

        matches = process.extractOne(query, list(memes.keys()), score_cutoff=67)
        if matches:
            best_match = matches[0]
            link = (
                memes[best_match][0]
                if "horny" in query.lower() and ctx.author.id == JORM_ID
                else random.choice(memes[best_match])
                if type(memes[best_match]) == list
                else memes[best_match]
            )
            await ctx.send(
                link,
                reference=ctx.message.reference,
                mention_author=False,
            )
        else:
            await ctx.send("Meme not found.")

    @commands.command(brief="Converts text into cyrillic", aliases=["cyrillic", "crlf"])
    async def cyrillify(self, ctx, *text):
        class ExampleLanguagePack(TranslitLanguagePack):
            language_code = "custom"
            language_name = "Custom"
            mapping = (
                "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwYyZz",
                "АаБбКкДдЕеФфГгХхИиЙйКкЛлМмНнОоПпКкРрСсТтУуВвУуЙйЗз",
            )
            pre_processor_mapping = {
                "scht": "щ",
                "sht": "щ",
                "sh": "ш",
                "tsch": "ч",
                "tch": "ч",
                "sch": "ш",
                "zh": "ж",
                "tz": "ц",
                "ch": "ч",
                "yu": "ю",
                "ya": "я",
                "x": "кс",
                "ck": "к",
                "ph": "ф",
            }
            chars = list(pre_processor_mapping.keys())
            for lat in chars:
                cyr = pre_processor_mapping[lat]
                pre_processor_mapping[lat.capitalize()] = cyr.capitalize()

        registry.register(ExampleLanguagePack)

        if not text:
            text = "Lorem ipsum dolor sit amet."
        else:
            text = " ".join(text)

        await ctx.send(translit(text, "custom"))

    @commands.command(brief="Burger someone")
    async def burger(self, ctx, target_mention):
        burgered = get_role(ctx.guild, "Burgered")
        if burgered and burgered in ctx.author.roles:
            if ctx.message.mentions:
                target = ctx.message.mentions[0]
                if target == ctx.author:
                    await ctx.send(
                        "You can't burger yourself - you are already burgered!"
                    )
                elif target.bot:
                    await ctx.send(
                        "Fool me once, shame on — shame on you. Fool me — you can't get fooled again."
                    )
                else:
                    await ctx.author.remove_roles(burgered)
                    await target.add_roles(burgered)
                    await ctx.send(target.mention)
                    await ctx.send(
                        "https://cdn.discordapp.com/attachments/744224801429782679/893950953378705508/unknown.png"
                    )

        else:
            await ctx.send("Only one who has been burgered may burger others.")

    @commands.group(brief="Add or rmeove vanity roles")
    async def vanity(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("vanity show"))

    @vanity.command(brief="Show all available vanity roles")
    async def show(self, ctx):

        vanity_roles = get_vanity_roles(ctx.guild)
        vanity_roles.sort(key=lambda x: x.name)

        embed = discord.Embed()
        embed.title = "Currently available vanity roles:"
        embed.description = (
            ", ".join([role.mention for role in vanity_roles]) + 2 * "\n"
        )
        embed.description += (
            "Type `+vanity pick [role]` or `+vanity remove` to change your vanity role"
        )
        await ctx.send(embed=embed)

    @vanity.command(brief="Pick a vanity role")
    async def pick(self, ctx, role):
        vanity_roles = get_vanity_roles(ctx.guild)
        role = get_role(ctx.guild, role)

        if role:
            if role in vanity_roles:
                if role not in ctx.author.roles:
                    await ctx.author.remove_roles(*vanity_roles)
                    await ctx.author.add_roles(role)
                else:
                    await ctx.send("You already have that role!")
            else:
                await ctx.send(
                    "You can only pick a vanity role. Type `+vanity show` to see the full list."
                )
        else:
            await ctx.send(
                "Please pick a valid vanity role. Type `+vanity show` to see the full list."
            )

    @vanity.command(brief="Remove your vanity role")
    async def remove(self, ctx, *role):
        vanity_roles = get_vanity_roles(ctx.guild)
        if role:
            role = get_role(ctx.guild, " ".join(role))
            if not role:
                await ctx.send(
                    "Please pick a valid vanity role, or leave blank to remove your current one. "
                    + "Type `+vanity show` to see the full list."
                )
            elif role in vanity_roles:
                await ctx.author.remove_roles(role)
            else:
                await ctx.send("You can only remove vanity roles.")
        else:
            await ctx.author.remove_roles(*vanity_roles)

    @commands.command(brief="Genererate a Pointing Farquaad meme")
    async def farquaad(self, ctx, *caption):
        img = Image.open(requests.get(memes["farquaad pointing"], stream=True).raw)
        draw = ImageDraw.Draw(img)

        font_path = str(Path(__file__).parent.parent.parent) + r"/fonts/impact.ttf"

        font = ImageFont.truetype(font=font_path, size=100)
        text = " ".join(caption).upper() if caption else ""
        width, height = draw.textsize(text, font)
        x_coord = img.width / 2 - width / 2
        y_coord = img.height - height - 25

        draw.text((x_coord - 3, y_coord - 3), text, (0, 0, 0), font=font)
        draw.text((x_coord + 3, y_coord - 3), text, (0, 0, 0), font=font)
        draw.text((x_coord + 3, y_coord + 3), text, (0, 0, 0), font=font)
        draw.text((x_coord - 3, y_coord + 3), text, (0, 0, 0), font=font)
        draw.text((x_coord, y_coord), text, (255, 255, 255), font=font)

        obj = io.BytesIO()
        img.save(obj, "png")
        obj.seek(0)

        await ctx.send(
            file=discord.File(obj, filename="Farquaad.png"),
            reference=ctx.message.reference if ctx.message.reference else None,
        )


def get_vanity_roles(guild):
    start, stop = [
        i for i in range(len(guild.roles)) if guild.roles[i].name == "Vanity"
    ][0:2]
    return guild.roles[start + 1 : stop]


def setup(bot):
    bot.add_cog(Fun(bot))
