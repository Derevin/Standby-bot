import datetime
import io
import json
import random
import sys
import traceback

import nextcord
import requests
from db.db_func import ensured_get_usr, get_or_insert_usr
from fuzzywuzzy import fuzz
from nextcord import Interaction, SlashOption
from nextcord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
from settings import *
from transliterate import translit
from transliterate.base import TranslitLanguagePack, registry
from utils.util_functions import *

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
        self.check_burger.start()

    def cog_unload(self):
        self.check_burger.cancel()

    @nextcord.slash_command(description="YEE")
    async def yee(self, interaction):
        await interaction.send(YEEE)

    @nextcord.slash_command(description="Gives a user a hug")
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

    @nextcord.user_command(name="Hug")
    async def hug_context(self, interaction, user):
        await invoke_slash_command("hug", self, interaction, user)

    @nextcord.slash_command(description="Pay your respects")
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

    @nextcord.slash_command(description="Posts a meme.")
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

    @nextcord.slash_command(description="Convert text into cyrillic")
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

    @nextcord.slash_command(description="Burger someone")
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
                expires = datetime.datetime.now() + BURGER_TIMEOUT
                await get_or_insert_usr(self.bot, target.id, interaction.guild.id)
                await self.bot.pg_pool.execute(
                    f"""DELETE FROM tmers WHERE ttype = {DB_TMER_BURGER};"""
                )
                await self.bot.pg_pool.execute(
                    """INSERT INTO tmers (usr_id, expires, ttype) """
                    """VALUES ($1, $2, $3);""",
                    target.id,
                    expires,
                    DB_TMER_BURGER,
                )
                await self.bot.pg_pool.execute(
                    f"UPDATE usr SET burgers = burgers + 1 WHERE usr_id = {target.id}"
                )
                history = await get_db_note(self.bot, "burger history")
                if history:
                    history = json.loads(history)
                    history = [target.id, *history[:4]]
                else:
                    history = [target.id]
                await log_or_update_db_note(self.bot, "burger history", history)
        else:
            if burgered.members:
                await interaction.send(
                    f"{burgered.members[0].mention} holds the burger - only they may burger others.",
                    ephemeral=True,
                )
            else:
                general = get_channel(interaction.guild, "general")
                await interaction.send(
                    f"The burger is currently free for the taking - to burger others, you must first claim it by answering the question in {general.mention}.",
                    ephemeral=True,
                )

    @nextcord.user_command(name="Burger")
    async def burger_context(self, interaction, user):
        await invoke_slash_command("burger", self, interaction, user)

    @tasks.loop(minutes=1)
    async def check_burger(self):
        try:
            gtable = await self.bot.pg_pool.fetch(
                f"SELECT * FROM tmers WHERE ttype = {DB_TMER_BURGER}"
            )
            for rec in gtable:
                if rec["ttype"] == DB_TMER_BURGER:
                    timenow = datetime.datetime.now()
                    if timenow <= rec["expires"]:
                        continue

                    print(f"record expired: {rec}")

                    guild = self.bot.get_guild(GUILD_ID)

                    if not guild:
                        print("no guild")
                        return

                    general = await guild.fetch_channel(GENERAL_ID)
                    user = await guild.fetch_member(rec["usr_id"])
                    burgered = get_role(guild, "Burgered")
                    if len(burgered.members) > 1:
                        maint = await guild.fetch_channel(ERROR_CHANNEL_ID)
                        await maint.send(
                            f"Multiple burgers detected: {', '.join([usr.mention for usr in burgered.members])}"
                        )

                    await user.remove_roles(burgered)

                    params = random.choice(BURGER_QUESTIONS)

                    answers = [*params["correct"], *params["wrong"]]
                    shuffled = answers.copy()
                    random.shuffle(shuffled)
                    params["ordering"] = [answers.index(elem) for elem in shuffled]
                    params["attempted"] = []

                    view = BurgerView(bot=self.bot, **params)
                    msg = await general.send(
                        (
                            f"After fending off the mold in {user.mention}'s fridge for a full week, the burger yearns for freedom!\n"
                            f"To claim it, answer the following question:\n \n{params['question']}"
                        ),
                        view=view,
                    )
                    await log_buttons(
                        self.bot,
                        view,
                        general.id,
                        msg.id,
                        json.dumps(params),
                    )
                    await self.bot.pg_pool.execute(
                        f"""DELETE FROM tmers WHERE ttype = {DB_TMER_BURGER};"""
                    )

        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return

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

    @nextcord.slash_command(description="Pick a vanity role")
    async def vanity(
        self,
        interaction: Interaction,
    ):
        view = self.VanityView(interaction.user)
        vanity_roles = get_roles_by_type(interaction.guild, "Vanity")
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

    @nextcord.slash_command(description="Genererate a captioned meme")
    async def caption(
        self,
        interaction: Interaction,
        template=SlashOption(
            description="The base template to caption", choices=["Farquaad", "Megamind"]
        ),
        caption=SlashOption(description="The caption to use"),
    ):
        await interaction.response.defer()

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

    @nextcord.slash_command(description="Praise toucan")
    async def praise(self, interaction):
        await interaction.send(TOUCAN_PRAISE)

    @nextcord.slash_command(description="Do you feel lucky?")
    async def roulette(self, interaction):

        cooldown = await self.bot.pg_pool.fetch(
            f"SELECT * FROM tmers WHERE usr_id = {interaction.user.id} AND ttype = {DB_TMER_ROULETTE}"
        )

        if cooldown:
            expires = cooldown[0]["expires"]
            if datetime.datetime.now() >= expires:
                await self.bot.pg_pool.execute(
                    f"DELETE FROM tmers WHERE usr_id = {interaction.user.id} AND ttype = {DB_TMER_ROULETTE}"
                )
            else:
                await interaction.send(
                    """You have been timed out from using this command. You will be able to use it again """
                    f"""{dynamic_timestamp(expires, 'delta')}""",
                    ephemeral=True,
                )
                return

        await interaction.response.defer()

        stats = await ensured_get_usr(self.bot, interaction.user.id, GUILD_ID)

        lose = random.randint(1, 6) == 6

        if lose:

            await self.bot.pg_pool.execute(
                f"""
            UPDATE usr
            SET current_roulette_streak = 0
            WHERE usr_id = {interaction.user.id}
            """
            )

            message = f"Not all risks pay off, {interaction.user.mention}. Your streak has been reset."
            try:
                await interaction.user.timeout(ROULETTE_TIMEOUT)
                message = message[:-1] + " and you have been timed out."
            except nextcord.errors.Forbidden:
                expires = datetime.datetime.now() + ROULETTE_TIMEOUT
                await self.bot.pg_pool.execute(
                    """INSERT INTO tmers (usr_id, expires, ttype) VALUES ($1, $2, $3);""",
                    interaction.user.id,
                    expires,
                    DB_TMER_ROULETTE,
                )

            await interaction.send(message)

        else:

            current_streak = stats[0]["current_roulette_streak"]
            max_streak = stats[0]["max_roulette_streak"]

            server_current_max = await self.bot.pg_pool.fetch(
                "SELECT MAX(current_roulette_streak) from usr"
            )
            server_current_max = server_current_max[0]["max"]

            server_alltime_max = await self.bot.pg_pool.fetch(
                "SELECT MAX(max_roulette_streak) from usr"
            )
            server_alltime_max = server_alltime_max[0]["max"]

            await self.bot.pg_pool.execute(
                f"""
                    UPDATE usr
                    SET current_roulette_streak = current_roulette_streak + 1,
                    max_roulette_streak = GREATEST(current_roulette_streak +1, max_roulette_streak)
                    WHERE usr_id = {interaction.user.id}
                    """
            )
            current_streak += 1

            plural_suffix = "s" if current_streak > 1 else ""

            message = f"Luck is on your side! You have now survived for {current_streak} round{plural_suffix} in a row"

            if current_streak > server_alltime_max:
                message += ", a new all-time record for the server!"
            elif current_streak > server_current_max and current_streak > max_streak:
                message += (
                    ", the highest currently active streak and a new personal best!"
                )
            elif current_streak > server_current_max:
                message += ", the highest currently active streak!"
            elif current_streak > max_streak:
                message += ", a new personal best!"
            else:
                message += "."

            await interaction.send(message)

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


class BurgerView(nextcord.ui.View):
    def __init__(self, **params):
        super().__init__(timeout=None)
        self.correct = params["correct"]
        self.attempted = params["attempted"]
        self.ordering = params["ordering"]
        answers = [*params["correct"], *params["wrong"]]
        bot = params["bot"]

        for index in self.ordering:
            self.add_item(self.BurgerButton(label=answers[index], bot=bot))

    class BurgerButton(nextcord.ui.Button):
        def __init__(self, label, bot):
            super().__init__(style=nextcord.ButtonStyle.blurple, label=label)
            self.bot = bot

        async def callback(self, interaction):
            if interaction.user.id in self.view.attempted:
                await interaction.send(
                    "You may only attempt to answer once", ephemeral=True
                )
                return

            if self.label in self.view.correct:
                await interaction.response.defer()
                burgered = get_role(interaction.guild, "Burgered")
                await interaction.user.add_roles(burgered)
                for child in self.view.children:
                    child.disabled = True
                await interaction.edit(
                    view=self.view,
                )
                await interaction.send(
                    f"{interaction.user.mention} has claimed the burger! Now use it wisely."
                )

                await get_or_insert_usr(
                    self.bot, interaction.user.id, interaction.guild.id
                )
                await self.bot.pg_pool.execute(
                    f"UPDATE usr SET burgers = burgers + 1 WHERE usr_id = {interaction.user.id}"
                )

                history = await get_db_note(self.bot, "burger history")
                if history:
                    history = json.loads(history)
                    mentions = [f"<@{user_id}>" for user_id in history]
                    if len(mentions) == 1:
                        msg = f"The last person to hold the burger is {mentions[0]}"
                    else:
                        msg = f"The last people to hold the burger are {','.join(mentions[:-1]) + ' and ' + mentions[-1]}"
                    await interaction.send(msg, ephemeral=True)
                    history = [interaction.user.id, *history[:4]]
                else:
                    history = [interaction.user.id]
                await self.bot.pg_pool.execute(
                    """INSERT INTO tmers (usr_id, expires, ttype) """
                    """VALUES ($1, $2, $3);""",
                    interaction.user.id,
                    datetime.datetime.now() + BURGER_TIMEOUT,
                    DB_TMER_BURGER,
                )
                await log_or_update_db_note(self.bot, "burger history", history)

            else:
                await interaction.send(
                    f"{self.label} is not the correct answer - better luck next time!",
                    ephemeral=True,
                )
                self.view.attempted.append(interaction.user.id)
                records = await self.bot.pg_pool.fetch(
                    f"SELECT params from buttons WHERE message_id = {interaction.message.id}"
                )
                params = records[0]["params"]
                params = json.loads(params)
                params["attempted"].append(interaction.user.id)
                params = json.dumps(params)
                await self.bot.pg_pool.execute(
                    f"UPDATE buttons SET params = '{params}' WHERE message_id = {interaction.message.id}"
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
