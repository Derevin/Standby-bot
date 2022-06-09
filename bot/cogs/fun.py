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
import datetime

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
            await interaction.send(GIT_STATIC_URL + "/images/selfhug.png")
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
        target=SlashOption(
            description="What do you want to pay your respects to?", required=False
        ),
    ):
        embed = nextcord.Embed()

        embed.description = f"{interaction.user.mention} has paid their respects."

        if target:
            text = target.split(" ")
            for index, word in enumerate(text):
                if not re.search(r"^<..?\d+>$", word):
                    text[index] = " ".join(word)

            bolded_text = "**" + "  ".join(text) + "**"

            embed.description = embed.description[:-1] + f" to {bolded_text}."

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
            all_memes = []
            for filename in os.listdir("static/images/memes"):
                parts = re.split(r"\.", filename)
                name = "".join(parts[:-1])
                extension = parts[-1]
                if re.search(r" \(\d+\)$", name):
                    stripped = re.split(r" \(\d+\)", name)[0]
                    all_memes.append(stripped)
                else:
                    all_memes.append(name)
            all_memes = list(set(all_memes))

            meme_names = "\n".join(sorted(all_memes, key=str.casefold))
            help_text = f"""Currently available memes:\n{meme_names}"""
            await interaction.response.send_message(
                f"```{help_text}```", ephemeral=True
            )
            return

        elif "horny" in query.lower() and interaction.user.id == FEL_ID:
            link = GIT_STATIC_URL + "/images/memes/Horny%20(2).png"
            await interaction.response.send_message(link)

        else:
            matches = []
            for filename in os.listdir("static/images/memes"):
                parts = re.split(r"\.", filename)
                name = "".join(parts[:-1])
                extension = parts[-1]

                if (
                    extension in ["jpg", "jpeg", "png", "gif"]
                    and fuzz.token_set_ratio(query, name) >= 67
                ):
                    matches.append((name, extension))

            if matches:
                meme = random.choice(matches)
                filename = meme[0] + "." + meme[1]
                link = GIT_STATIC_URL + "/images/memes/" + re.sub(" ", "%20", filename)
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
                await interaction.channel.send(GIT_STATIC_URL + "/images/burgered.png")

        else:
            await interaction.send(
                "Only one who has been burgered may burger others.", ephemeral=True
            )

    class VanityView(nextcord.ui.View):
        def __init__(self, creator):
            super().__init__()
            self.value = None
            self.creator = creator

        @nextcord.ui.select(placeholder="Pick a vanity role")
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
            query, font_size, align = "Farquaad pointing", 100, "bottom"
        elif template == "Megamind":
            query, font_size, align = "Megamind no bitches", 125, "top"

        img = Image.open(
            requests.get(GIT_STATIC_URL + f"/images/memes/{query}.png", stream=True).raw
        )
        draw = ImageDraw.Draw(img)

        font_path = get_local_static_path() + "/fonts/impact.ttf"

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

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Praise toucan")
    async def praise(self, interaction):
        await interaction.send(TOUCAN_PRAISE)

    @nextcord.slash_command(guild_ids=[GUILD_ID], description="Do you feel lucky?")
    async def roulette(self, interaction):

        await interaction.response.defer()

        lose = random.randint(1, 6) == 6

        exists = await self.bot.pg_pool.fetch(
            f"SELECT * FROM usr WHERE usr_id = {interaction.user.id}"
        )

        if not exists:
            await self.bot.pg_pool.execute(
                f"""
            INSERT INTO 'usr' (usr_id, guild_id, roulette_streak)
            VALUES ({interaction.user.id}, {GUILD_ID}, 0)
            """
            )

        if lose:

            await self.bot.pg_pool.execute(
                f"""
            UPDATE usr
            SET roulette_streak = 0
            WHERE usr_id = {interaction.user.id}
            """
            )

            message = f"Not all risks pay off, {interaction.user.mention}. Your streak has been reset."
            try:
                await interaction.user.timeout(datetime.timedelta(minutes=30))
                message = message[:-1] + " and you have been timed out."
            except nextcord.errors.Forbidden:
                print("abc")
                pass
            await interaction.send(message)

        else:

            await self.bot.pg_pool.execute(
                f"""
            UPDATE usr
            SET roulette_streak = roulette_streak + 1
            WHERE usr_id = {interaction.user.id}
            """
            )

            current_streak = exists[0]["roulette_streak"] + 1 if exists else 1
            plural_suffix = "s" if current_streak > 1 else ""

            await interaction.send(
                f"Luck is on your side. You have now survived for {current_streak} round{plural_suffix} in a row."
            )

    class YesOrNo(nextcord.ui.View):
        def __init__(self, intended_user):
            super().__init__()
            self.value = None
            self.yes = None
            self.intended_user = intended_user

        @nextcord.ui.button(
            label="Yes",
            style=nextcord.ButtonStyle.green,
        )
        async def yes_button(self, button: nextcord.ui.Button, interaction=Interaction):

            if interaction.user == self.intended_user:
                self.yes = True
                self.stop()
            else:
                await interaction.send(
                    GIT_STATIC_URL + "/images/bobby.gif",
                    ephemeral=True,
                )

        @nextcord.ui.button(label="No", style=nextcord.ButtonStyle.red)
        async def no_button(self, button: nextcord.ui.Button, interaction=Interaction):

            if interaction.user == self.intended_user:
                self.yes = False
                self.stop()
            else:
                await interaction.send(
                    GIT_STATIC_URL + "/images/bobby.gif",
                    ephemeral=True,
                )

    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):

    #     if before.id != FEL_ID:
    #         return

    #     if before.display_name == after.display_name:
    #         return

    #     if not re.search("fel", after.display_name, re.I):
    #         return

    #     new_name = re.sub(
    #         r"(?<=fe)l",
    #         lambda l: "n" if l.group(0).islower() else "N",
    #         after.display_name,
    #         flags=re.I,
    #     )

    #     try:
    #         guild = await self.bot.fetch_guild(GUILD_ID)
    #     except Exception:
    #         pass

    #     if not guild:
    #         return

    #     FEN_ID = 292588333773750273
    #     fen = await guild.fetch_member(FEN_ID)
    #     fel = await guild.fetch_member(FEL_ID)

    #     general = self.bot.get_channel(GENERAL_ID)

    #     view = self.YesOrNo(intended_user=fen)

    #     ask = await general.send(
    #         f"Hey {fen.mention}, do you want to change your name to match {fel.mention}?",
    #         view=view,
    #     )

    #     await view.wait()
    #     await ask.edit(view=None)
    #     if view.yes:
    #         aww = get_emoji(guild, "BlobAww")
    #         await general.send(f"Twinsies!{' ' + aww if aww else ''}")
    #         await fen.edit(nick=new_name)
    #     else:
    #         ok = get_emoji(guild, "JoxOK")
    #         await general.send(ok if ok else "👍")


def setup(bot):
    bot.add_cog(Fun(bot))
