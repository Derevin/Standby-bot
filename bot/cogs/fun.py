from nextcord.ext import commands, application_checks
import nextcord
from nextcord import Interaction, SlashOption
import random
from utils.util_functions import *
from settings import *
from fuzzywuzzy import process, fuzz
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
    "Silence, brand": "https://cdn.discordapp.com/attachments/744224801429782679/915240126190350416/unknown.png",
    "I am looking away, I do not see it": (
        "https://cdn.discordapp.com/attachments/744224801429782679/918249653412167690/unknown.png"
    ),
    "Chadoru": "https://cdn.discordapp.com/attachments/744224801429782679/919260111250280468/padoruchad.png",
    "Jesse, what the fuck are you talking about": [
        "https://cdn.discordapp.com/attachments/744224801429782679/934550870681595935/unknown.png",
        "https://cdn.discordapp.com/attachments/744224801429782679/934551037761716234/unknown.png",
    ],
    "They hated Jesus because he told them the truth": (
        "https://cdn.discordapp.com/attachments/744224801429782679/943556748734771260/unknown.png"
    ),
    "Megamind No bitches?": "https://cdn.discordapp.com/attachments/744224801429782679/950791113487319070/unknown.png",
    "Live Kross reaction": "https://cdn.discordapp.com/attachments/744224801429782679/962417461192441896/kross.gif",
}

meme_names = "\n".join(sorted(list(memes.keys()), key=str.casefold))
help_text = f"""
Currently available memes:\n{meme_names}
"""


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="YEE")
    async def yee(self, interaction):
        await interaction.send(YEEE)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Gives a user a hug")
    async def hug(
        self,
        interaction: Interaction,
        user: nextcord.User = SlashOption(
            description="The user you want to send a hug to"
        ),
    ):
        if user == interaction.user:
            await interaction.send(
                "https://cdn.discordapp.com/attachments/744224801429782679/757549246533599292/selfhug.png"
            )
        else:
            await interaction.send(
                f"{user.mention}, {interaction.user.mention} sent you a hug!"
            )
            hug = get_emoji(interaction.guild, "BlobReachAndHug")
            if hug:
                await interaction.channel.send(hug)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Pay your respects")
    async def f(
        self,
        interaction: Interaction,
        target=SlashOption(description="What do you want to pay your respects to?"),
    ):
        embed = nextcord.Embed()
        embed.description = (
            f"**{interaction.user.name}** has paid their respects"
            + (f" to **{' '.join(target)}**" if target else "")
            + "."
        )
        await interaction.response.send_message(embed=embed)
        rip = await interaction.original_message()
        await rip.add_reaction("🇫")

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Posts a meme.")
    async def meme(
        self,
        interaction: Interaction,
        query: str = SlashOption(
            name="search_term",
            description="Enter a search term for the meme you want to post",
        ),
    ):
        if query == "help":
            await interaction.response.send_message(
                f"```{help_text}```", ephemeral=True
            )
            return

        matches = process.extractOne(
            query, list(memes.keys()), scorer=fuzz.token_set_ratio, score_cutoff=67
        )
        if matches:
            best_match = matches[0]
            link = (
                memes[best_match][0]
                if "horny" in query.lower() and interaction.user.id == FEL_ID
                else random.choice(memes[best_match])
                if type(memes[best_match]) == list
                else memes[best_match]
            )
            await interaction.response.send_message(link)

        else:
            await interaction.response.send_message(
                f"No match found for '{query}' - use `/meme help` to see list of available memes.",
                ephemeral=True,
            )

    @nextcord.slash_command(
        guild_ids=[GUILD_ID], description="Convert text into cyrillic"
    )
    async def cyrillify(
        self,
        interaction: Interaction,
        text=SlashOption(description="Text to cyrillify"),
    ):
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

        await interaction.send(translit(text, "custom"))

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Burger someone")
    async def burger(
        self,
        interaction: Interaction,
        target: nextcord.User = SlashOption(
            description="The person you want to burger"
        ),
    ):
        burgered = get_role(interaction.guild, "Burgered")
        if burgered and burgered in interaction.user.roles:
            if target == interaction.user:
                await interaction.send(
                    "You can't burger yourself - you are already burgered!",
                    ephemeral=True,
                )
            elif target.bot:
                await interaction.send(
                    "Fool me once, shame on — shame on you. Fool me — you can't get fooled again.",
                    ephemeral=True,
                )
            else:
                await interaction.user.remove_roles(burgered)
                await target.add_roles(burgered)
                await interaction.send(target.mention)
                await interaction.channel.send(
                    "https://cdn.discordapp.com/attachments/744224801429782679/893950953378705508/unknown.png"
                )

        else:
            await interaction.send(
                "Only one who has been burgered may burger others.", ephemeral=True
            )

    # @nextcord.slash_command(guild_ids=[GUILD_ID])
    # async def vanity(self, interaction: Interaction):
    #     pass

    # @vanity.subcommand(description="Show all available vanity roles")
    # async def show(self, interaction: Interaction):

    #     vanity_roles = get_vanity_roles(interaction.guild)
    #     vanity_roles.sort(key=lambda x: x.name)

    #     embed = nextcord.Embed()
    #     embed.title = "Currently available vanity roles:"
    #     embed.description = (
    #         ", ".join([role.mention for role in vanity_roles]) + 2 * "\n"
    #     )
    #     embed.description += "Use `/vanity` to change your vanity role"
    #     await interaction.send(embed=embed)

    class VanityView(nextcord.ui.View):
        def __init__(self, creator):
            super().__init__()
            self.value = None
            self.creator = creator

        @nextcord.ui.select(placeholder="Pick a vanity role", min_values=0)
        async def select_role(
            self, select: nextcord.ui.Select, interaction: Interaction
        ):
            if self.creator == interaction.user and select.values:
                self.value = select.values[0]

        @nextcord.ui.button(
            label="Pick",
            style=nextcord.ButtonStyle.blurple,
        )
        async def press(self, button: nextcord.ui.Button, interaction=Interaction):

            if self.creator == interaction.user and self.value:
                self.stop()

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Pick a vanity role")
    async def vanity(
        self,
        interaction: Interaction,
    ):
        view = self.VanityView(interaction.user)
        vanity_roles = get_vanity_roles(interaction.guild)
        for role in vanity_roles:
            view.children[0].add_option(label=role.name)
        view.children[0].add_option(label="Remove my vanity role", value="remove")
        await interaction.send(view=view)
        await view.wait()
        if view.value:
            await interaction.user.remove_roles(*vanity_roles)
            text = "Your vanity role has been removed."
            if view.value != "remove":
                role = get_role(interaction.guild, view.value)
                await interaction.user.add_roles(role)
                text = f"You are now (a) {role.name}."
            msg = await interaction.original_message()
            await msg.edit(text, view=None, delete_after=10)

    @nextcord.slash_command(
        guild_ids=[GUILD_ID], description="Genererate a captioned meme"
    )
    async def caption(
        self,
        interaction: Interaction,
        template=SlashOption(
            description="The base template to caption", choices=["Farquaad", "Megamind"]
        ),
        caption=SlashOption(description="The caption to use"),
    ):

        if template == "Farquaad":
            query, font_size, align = "farquaad pointing", 100, "bottom"
        elif template == "Megamind":
            query, font_size, align = "Megamind No bitches?", 125, "top"

        img = Image.open(requests.get(memes[query], stream=True).raw)
        draw = ImageDraw.Draw(img)

        font_path = str(Path(__file__).parent.parent.parent) + r"/fonts/impact.ttf"

        font = ImageFont.truetype(font=font_path, size=font_size)
        text = caption.upper()
        width, height = draw.textsize(text, font)
        x_coord = img.width / 2 - width / 2
        y_coord = img.height - height - 25 if align == "bottom" else 0

        draw.text((x_coord - 3, y_coord - 3), text, (0, 0, 0), font=font)
        draw.text((x_coord + 3, y_coord - 3), text, (0, 0, 0), font=font)
        draw.text((x_coord + 3, y_coord + 3), text, (0, 0, 0), font=font)
        draw.text((x_coord - 3, y_coord + 3), text, (0, 0, 0), font=font)
        draw.text((x_coord, y_coord), text, (255, 255, 255), font=font)

        obj = io.BytesIO()
        img.save(obj, "png")
        obj.seek(0)

        await interaction.send(
            file=nextcord.File(obj, filename=f"{template}.png"),
        )

    @nextcord.slash_command(
        guild_ids=[GUILD_ID],
        name="8ball",
        description="Provides a Magic 8-Ball answer to a yes/no question",
    )
    async def eightball(
        self,
        interaction: Interaction,
        question=SlashOption(description="What is your question?"),
    ):
        answers = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        await interaction.send(random.choice(answers))


def setup(bot):
    bot.add_cog(Fun(bot))
