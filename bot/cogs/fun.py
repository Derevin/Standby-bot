import io
import json
import os
import random
import re
from datetime import datetime as dt
from itertools import permutations

import aiohttp
import nextcord
import requests
from PIL import Image, ImageDraw, ImageFont
from fuzzywuzzy import fuzz
from nextcord import ButtonStyle, Embed, Member, SlashOption, slash_command, ui, user_command
from nextcord.ext.commands import Cog
from transliterate import translit
from transliterate.base import TranslitLanguagePack, registry

from config.constants import *
from db_integration import db_functions as db
from utils import util_functions as uf

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


def add(lhs: int, rhs: int, pstr: str):
    return lhs + rhs, pstr + "+" + str(rhs)


def sub(lhs: int, rhs: int, pstr: str):
    return lhs - rhs, pstr + "-" + str(rhs)


def mult(lhs: int, rhs: int, pstr: str):
    if rhs == 0:
        return 0, ""
    return lhs * rhs, "(" + pstr + ")*" + str(rhs)


def div(lhs: int, rhs: int, pstr: str):
    return lhs / rhs, "(" + pstr + ")/" + str(rhs)


operations = [add, sub, mult, div]


def create_concat_combinations(digits):
    combs = [digits.copy()]
    for tupling_sz in range(2, len(digits) + 1):
        for num_tupling in range(1, int(len(digits) / tupling_sz) + 1):
            perms = permutations(digits)
            for perm in perms:
                out = list(perm).copy()
                coupled = []
                for i in range(num_tupling):
                    to_merge = perm[i * tupling_sz: i * tupling_sz + tupling_sz]
                    merged = int("".join(map(str, to_merge)))
                    coupled.append(merged)
                    out = out[i * tupling_sz + tupling_sz:]
                out.extend(coupled)
                combs.append(out)

    for i in range(len(combs)):
        combs[i] = sorted(combs[i])

    filtered_combs = []
    for comb in combs:
        if comb not in filtered_combs:
            filtered_combs.append(comb)
    return filtered_combs


async def dfs(target, current_target, current_digits, current_str):
    if current_target == target:
        return current_str

    if not current_digits:
        return ""

    for dig in current_digits:
        new_digits = current_digits.copy()
        new_digits.remove(dig)
        for op in operations:
            if op == div and dig == 0:
                continue
            new_target, new_str = op(current_target, dig, current_str)
            if op == div and not new_target.is_integer():
                continue
            res = await dfs(target, int(new_target), new_digits, new_str)
            if res:
                return res

    return ""


class Fun(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.check_burger.start()


    def cog_unload(self):
        self.check_burger.cancel()


    @slash_command(description="YEE")
    async def yee(self, interaction):
        await interaction.send(YEEE)


    @slash_command(description="Gives a user a hug")
    async def hug(self, interaction, user: Member = SlashOption(description="The user you want to send a hug to")):
        if user == interaction.user:
            await interaction.send(GIT_STATIC_URL + "/images/selfhug.png")
        else:
            await interaction.send(f"{user.mention}, {interaction.user.mention} sent you a hug!")
            hug = uf.get_emoji(interaction.guild, "BlobReachAndHug")
            if hug:
                await interaction.channel.send(hug)


    @user_command(name="Hug")
    async def hug_context(self, interaction, user):
        await uf.invoke_slash_command("hug", self, interaction, user)


    @slash_command(description="Pay your respects")
    async def f(self, interaction,
                target: str = SlashOption(description="What do you want to pay your respects to?", required=False)):
        embed = Embed()

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


    @slash_command(description="Posts a meme.")
    async def meme(self, interaction,
                   query: str = SlashOption(name="search_term", description="Enter a search term for the "
                                                                            "meme you want to post")):
        if query == "help":
            all_memes = []
            for filename in os.listdir("static/images/memes"):
                parts = re.split(r"\.", filename)
                name = "".join(parts[:-1])
                if re.search(r" \(\d+\)$", name):
                    stripped = re.split(r" \(\d+\)", name)[0]
                    all_memes.append(stripped)
                else:
                    all_memes.append(name)
            all_memes = sorted(set(all_memes), key=str.casefold)
            meme_names = "\n".join(all_memes)
            help_text = f"Currently available memes:\n{meme_names}"
            await interaction.response.send_message(f"```{help_text}```", ephemeral=True)
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
                if extension in ["jpg", "jpeg", "png", "gif"] and fuzz.token_set_ratio(query, name) >= 67:
                    matches.append((name, extension))

            if matches:
                meme = random.choice(matches)
                filename = meme[0] + "." + meme[1]
                link = GIT_STATIC_URL + "/images/memes/" + re.sub(" ", "%20", filename)
                await interaction.response.send_message(link)

            else:
                await db.log(self.bot, f"No matching meme found for {query=}")
                await interaction.response.send_message(f"No match found for '{query}' - use `/meme help` "
                                                        "to see list of available memes.", ephemeral=True)


    @slash_command(description="Convert text into cyrillic")
    async def cyrillify(self, interaction, text: str = SlashOption(description="Text to cyrillify")):
        class ExampleLanguagePack(TranslitLanguagePack):
            language_code = "custom"
            language_name = "Custom"
            latin = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwYyZz"
            cyrillic = "АаБбКкДдЕеФфГгХхИиЙйКкЛлМмНнОоПпКкРрСсТтУуВвУуЙйЗз"
            mapping = latin, cyrillic
            pre_processor_mapping = {"scht": "щ", "sht": "щ", "sh": "ш", "tsch": "ч", "tch": "ч", "sch": "ш", "zh": "ж",
                                     "tz": "ц", "ch": "ч", "yu": "ю", "ya": "я", "x": "кс", "ck": "к", "ph": "ф", }
            chars = list(pre_processor_mapping.keys())
            for lat in chars:
                cyr = pre_processor_mapping[lat]
                pre_processor_mapping[lat.capitalize()] = cyr.capitalize()

        registry.register(ExampleLanguagePack)

        await interaction.send(translit(text, "custom"))


    @slash_command(description="Burger someone")
    async def burger(self, interaction, target: Member = SlashOption(description="The person you want to burger")):
        burgered = uf.get_role(interaction.guild, "Burgered")
        if burgered and burgered in interaction.user.roles:
            if target == interaction.user:
                await interaction.send("You can't burger yourself - you are already burgered!", ephemeral=True)
            elif target.bot:
                await interaction.send("Fool me once, shame on — shame on you. Fool me — you can't get fooled again.",
                                       ephemeral=True)
            else:
                await interaction.user.remove_roles(burgered)
                await target.add_roles(burgered)
                await interaction.send(target.mention)
                await interaction.channel.send(GIT_STATIC_URL + "/images/burgered.png")
                expires = dt.now() + BURGER_TIMEOUT
                await db.get_or_insert_usr(self.bot, target.id, interaction.guild.id)
                await self.bot.pg_pool.execute(f"DELETE FROM tmers WHERE ttype = {DB_TMER_BURGER};")
                await self.bot.pg_pool.execute("INSERT INTO tmers (usr_id, expires, ttype) VALUES ($1, $2, $3);",
                                               target.id, expires, DB_TMER_BURGER)
                await self.bot.pg_pool.execute(f"UPDATE usr SET burgers = burgers + 1 WHERE usr_id = {target.id}")
                history = await db.get_note(self.bot, "burger history")
                if history:
                    history = json.loads(history)
                    history = [target.id, *history[:4]]
                else:
                    history = [target.id]
                await db.log_or_update_note(self.bot, "burger history", history)
        else:
            if burgered.members:
                await interaction.send(f"{burgered.members[0].mention} holds the burger - only they may burger others.",
                                       ephemeral=True)
            else:
                general = uf.get_channel(interaction.guild, "general")
                await interaction.send("The burger is currently free for the taking - to burger others, you must first "
                                       f"claim it by answering the question in {general.mention}.", ephemeral=True)


    @user_command(name="Burger")
    async def burger_context(self, interaction, user):
        await uf.invoke_slash_command("burger", self, interaction, user)


    @uf.delayed_loop(minutes=1)
    async def check_burger(self):
        try:
            gtable = await self.bot.pg_pool.fetch(f"SELECT * FROM tmers WHERE ttype = {DB_TMER_BURGER}")
            for rec in gtable:
                timenow = dt.now()
                if timenow <= rec["expires"]:
                    continue

                guild = self.bot.get_guild(GUILD_ID)

                if not guild:
                    await db.log(self.bot, "Could not fetch guild")
                    return
                general = await guild.fetch_channel(GENERAL_ID)
                user = await guild.fetch_member(rec["usr_id"])
                burgered = uf.get_role(guild, "Burgered")
                if len(burgered.members) > 1:
                    maint = await guild.fetch_channel(ERROR_CHANNEL_ID)
                    await maint.send(
                        f"Multiple burgers detected: {', '.join([usr.mention for usr in burgered.members])}")

                await user.remove_roles(burgered)
                try:
                    response = requests.get("https://the-trivia-api.com/v2/questions?limit=1")
                    data = json.loads(response.text)[0]
                    params = {"question": data["question"]["text"], "correct": [data["correctAnswer"]],
                              "wrong": data["incorrectAnswers"], }
                except Exception:
                    await db.log(self.bot, "Invalid response from Trivia API")
                    params = random.choice(BURGER_QUESTIONS)

                answers = [*params["correct"], *params["wrong"]]
                shuffled = answers.copy()
                random.shuffle(shuffled)
                params["ordering"] = [answers.index(elem) for elem in shuffled]
                params["attempted"] = []
                params["last_owner_id"] = user.id
                view = BurgerView(bot=self.bot, **params)

                recs = await self.bot.pg_pool.fetch(f"SELECT moldy_burgers FROM usr WHERE usr_id = {user.id}")
                if not recs:
                    count = 1
                else:
                    count = recs[0]["moldy_burgers"] + 1
                await self.bot.pg_pool.execute(f"UPDATE usr SET moldy_burgers = {count} WHERE usr_id = {user.id}")

                msg = await general.send(f"After its {count}{uf.ordinal_suffix(count)} bout of fending off the mold in"
                                         f"{user.mention}'s fridge for a full week, the burger yearns for freedom!\n"
                                         f"To claim it, answer the following question:\n \n"
                                         f"{params['question']}",
                                         view=view)
                await db.log_buttons(self.bot, view, general.id, msg.id, params)
                await self.bot.pg_pool.execute(f"DELETE FROM tmers WHERE ttype = {DB_TMER_BURGER};")

        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception as e:
            await db.log(self.bot, f"Unexpected exception: {e}")
            return


    @slash_command(description="Make predictions")
    async def prediction(self, interaction):
        pass


    @prediction.subcommand(description="Make a prediction")
    async def make(self, interaction, label: str = SlashOption(description="A label to identify your prediction"),
                   text: str = SlashOption(description="The text of your prediction")):
        predictions = await uf.get_user_predictions(self.bot, interaction.user)

        if label in predictions:
            num = len([key for key in predictions if key.startswith(label + "_")])
            label = f"{label}_{num + 2}"

        predictions[label] = {"timestamp": uf.dynamic_timestamp(uf.now(), "date and time"), "text": text}

        await uf.update_user_predictions(self.bot, interaction.user, predictions)
        await interaction.send(f"Prediction saved with label '{label}'!", ephemeral=True),
        await interaction.channel.send(f"{interaction.user.mention} just made a prediction!")


    @prediction.subcommand(description="Reveal a prediction")
    async def reveal(self, interaction, label: str = SlashOption(description="Label of the prediction to reveal")):
        predictions = await uf.get_user_predictions(self.bot, interaction.user)
        if label in predictions:
            params = {"owner_id": interaction.user.id, "votes_for": [], "votes_against": []}
            view = PredictionView(bot=self.bot, **params)
            await interaction.send(f"On {predictions[label]['timestamp']}, {interaction.user.mention} made the "
                                   f"following prediction:\n{EMPTY}\n"
                                   f"{predictions[label]['text']}\n{EMPTY}\n"
                                   f"Does this prediction deserve an 🔮? Vote below!", view=view)
            msg = await interaction.original_message()
            await db.log_buttons(self.bot, view, interaction.channel.id, msg.id, params)
            predictions.pop(label)
            await uf.update_user_predictions(self.bot, interaction.user, predictions)
        else:
            await interaction.send(f"No prediction found for the label '{label}'. You can use `/prediction list` "
                                   "to see a list of your active predictions.", ephemeral=True)


    @prediction.subcommand(description="Check a prediction (privately)")
    async def check(self, interaction,
                    label: str = SlashOption(description="Label of the prediction you want to check")):
        predictions = await uf.get_user_predictions(self.bot, interaction.user)
        if label in predictions:
            await interaction.send(f"Prediction '{label}' made on {predictions[label]['timestamp']}:\n{EMPTY}\n"
                                   f"{predictions[label]['text']}", ephemeral=True)
        else:
            await interaction.send(f"No prediction found for the label '{label}'. You can use `/prediction list` "
                                   "to see a list of your active predictions.", ephemeral=True)


    @prediction.subcommand(name="list", description="List your predictions (privately)")
    async def list_(self, interaction):
        predictions = await uf.get_user_predictions(self.bot, interaction.user)
        if not predictions:
            await interaction.send("You have not made any predictions!", ephemeral=True)
        else:
            for label, prediction in predictions.items():
                await interaction.send(f"Prediction '{label}' made on {prediction['timestamp']}:\n{EMPTY}\n"
                                       f"{prediction['text']}", ephemeral=True)


    @prediction.subcommand(description="Delete a prediction")
    async def delete(self, interaction, label: str = SlashOption(description="Label of the prediction to delete")):
        predictions = await uf.get_user_predictions(self.bot, interaction.user)
        if label in predictions:
            predictions.pop(label)
            await uf.update_user_predictions(self.bot, interaction.user, predictions)
            await interaction.send(f"Prediction '{label}' successfully deleted!", ephemeral=True)
        else:
            await interaction.send(f"No prediction found for the label '{label}'!")

    class VanityView(ui.View):

        def __init__(self, creator):
            super().__init__()
            self.value = None
            self.creator = creator


        @ui.select(placeholder="Pick a vanity role")
        async def select_role(self, select: ui.Select, interaction):
            if self.creator == interaction.user and select.values:
                self.value = select.values[0]


        @ui.button(label="Pick", style=ButtonStyle.blurple)
        async def press(self, button, interaction):
            if self.creator == interaction.user and self.value:
                self.stop()

    @slash_command(description="Pick a vanity role")
    async def vanity(self, interaction):
        view = self.VanityView(interaction.user)
        vanity_roles = uf.get_roles_by_type(interaction.guild, "Vanity")
        for role in vanity_roles:
            view.children[0].add_option(label=role.name)
        view.children[0].add_option(label="Remove my vanity role", value="remove")
        await interaction.send(view=view)
        await view.wait()
        if view.value:
            await interaction.user.remove_roles(*vanity_roles)
            text = "Your vanity role has been removed."
            if view.value != "remove":
                role = uf.get_role(interaction.guild, view.value)
                await interaction.user.add_roles(role)
                text = f"You are now (a) {role.name}."
            msg = await interaction.original_message()
            await msg.edit(text, view=None, delete_after=10)


    @slash_command(description="Genererate a captioned meme")
    async def caption(self, interaction, caption: str = SlashOption(description="The caption to use"),
                      template: str = SlashOption(description="The base template to caption",
                                                  choices=["Farquaad", "Megamind"])):
        await interaction.response.defer()

        if template == "Farquaad":
            query, font_size, align = "Farquaad pointing", 100, "bottom"
        else:  # template == "Megamind":
            query, font_size, align = "Megamind no bitches", 125, "top"

        img = Image.open(requests.get(GIT_STATIC_URL + f"/images/memes/{query}.png", stream=True).raw)
        draw = ImageDraw.Draw(img)

        font_path = LOCAL_STATIC_PATH / "fonts" / "impact.ttf"

        font = ImageFont.truetype(font=str(font_path), size=font_size)
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

        await interaction.send(file=nextcord.File(obj, filename=f"{template}.png"))


    @slash_command(name="8ball", description="Provides a Magic 8-Ball answer to a yes/no question")
    async def eightball(self, interaction, question=SlashOption(description="What is your question?")):
        answers = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
                   "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.",
                   "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
                   "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
                   "My sources say no.", "Outlook not so good.", "Very doubtful."]
        await interaction.send(random.choice(answers))


    @slash_command(description="Praise toucan")
    async def praise(self, interaction):
        await interaction.send(TOUCAN_PRAISE)


    @slash_command(description="Do you feel lucky?")
    async def roulette(self, interaction):
        cooldown = await self.bot.pg_pool.fetch(
            f"SELECT * FROM tmers WHERE usr_id = {interaction.user.id} AND ttype = {DB_TMER_ROULETTE}")

        if cooldown:
            expires = cooldown[0]["expires"]
            if dt.now() >= expires:
                await self.bot.pg_pool.execute(
                    f"DELETE FROM tmers WHERE usr_id = {interaction.user.id} AND ttype = {DB_TMER_ROULETTE}")
            else:
                await interaction.send(
                    "You have been timed out from using this command. You will be able to use it again "
                    f"{uf.dynamic_timestamp(expires, 'relative')}", ephemeral=True)
                return

        await interaction.response.defer()

        stats = await db.ensured_get_usr(self.bot, interaction.user.id, GUILD_ID)
        lose = random.randint(1, 6) == 6

        if lose:
            await self.bot.pg_pool.execute(
                f"UPDATE usr SET current_roulette_streak = 0 WHERE usr_id = {interaction.user.id}")

            message = f"Not all risks pay off, {interaction.user.mention}. Your streak has been reset."
            try:
                await interaction.user.timeout(ROULETTE_TIMEOUT)
                message = message[:-1] + " and you have been timed out."
            except nextcord.errors.Forbidden:
                expires = dt.now() + ROULETTE_TIMEOUT
                await self.bot.pg_pool.execute("INSERT INTO tmers (usr_id, expires, ttype) VALUES ($1, $2, $3);",
                                               interaction.user.id, expires, DB_TMER_ROULETTE)
            await interaction.send(message)

        else:
            current_streak = stats[0]["current_roulette_streak"]
            max_streak = stats[0]["max_roulette_streak"]

            server_current_max = await self.bot.pg_pool.fetch("SELECT MAX(current_roulette_streak) from usr")
            server_current_max = server_current_max[0]["max"]

            server_alltime_max = await self.bot.pg_pool.fetch("SELECT MAX(max_roulette_streak) from usr")
            server_alltime_max = server_alltime_max[0]["max"]

            await self.bot.pg_pool.execute("UPDATE usr SET current_roulette_streak = current_roulette_streak + 1,"
                                           "max_roulette_streak = "
                                           "GREATEST(current_roulette_streak + 1, max_roulette_streak) "
                                           f"WHERE usr_id = {interaction.user.id}")
            current_streak += 1

            plural_suffix = "s" if current_streak > 1 else ""

            message = f"Luck is on your side! You have now survived for {current_streak} round{plural_suffix} in a row"

            if current_streak > server_alltime_max:
                message += ", a new all-time record for the server!"
            elif current_streak > server_current_max and current_streak > max_streak:
                message += ", the highest currently active streak and a new personal best!"
            elif current_streak > server_current_max:
                message += ", the highest currently active streak!"
            elif current_streak > max_streak:
                message += ", a new personal best!"
            else:
                message += "."

            await interaction.send(message)


    @slash_command(description="Calculates how to 'math' a target number from given digits")
    async def fabricate_number(self, interaction, wanted_result, comma_separated_digits):
        try:
            target = int(wanted_result)
            digits = [int(i) for i in comma_separated_digits.split(",")]
        except Exception as e:
            await interaction.send(f"Bad input {e}")
            return

        if not digits or target == 0:
            await interaction.send("Bad input - target must be non-zero and at least one digit must be provided")
            return

        await interaction.response.defer()

        concatenations = create_concat_combinations(digits)
        num_digit_combinations = len(concatenations)
        did_cut = False
        attempt_limit = 50000
        if num_digit_combinations > attempt_limit:  # make sure someone doesn't super bomb it
            concatenations = concatenations[:attempt_limit]
            did_cut = True

        for concat_digits in concatenations:
            for dig in concat_digits:
                new_digits = concat_digits.copy()
                new_digits.remove(dig)
                res = await dfs(target, dig, new_digits, str(dig))
                if res:
                    msg = f"`{target}` from `{digits}` can be 'mathed' out this way:`{res}`"
                    await interaction.send(msg)
                    return

        if did_cut:
            await interaction.send(f"Nothing found in {attempt_limit}/{num_digit_combinations} combinations")
        else:
            await interaction.send(f"Nothing found in {num_digit_combinations} combinations")

    class YesOrNo(ui.View):

        def __init__(self, intended_user):
            super().__init__()
            self.value = None
            self.yes = None
            self.intended_user = intended_user


        @ui.button(label="Yes", style=ButtonStyle.green)
        async def yes_button(self, button, interaction):
            if interaction.user == self.intended_user:
                self.yes = True
                self.stop()
            else:
                await interaction.send(GIT_STATIC_URL + "/images/bobby.gif", ephemeral=True)


        @ui.button(label="No", style=ButtonStyle.red)
        async def no_button(self, button, interaction):
            if interaction.user == self.intended_user:
                self.yes = False
                self.stop()
            else:
                await interaction.send(GIT_STATIC_URL + "/images/bobby.gif", ephemeral=True)

    @user_command(name="Thank", guild_ids=[GUILD_ID])
    async def thank_context(self, interaction, user):
        if user == interaction.user:
            await interaction.send("Thanking yourself gives no reputation.", ephemeral=True)
            return

        await db.get_or_insert_usr(self.bot, user.id, interaction.guild.id)
        await self.bot.pg_pool.execute(f"UPDATE usr SET thanks = thanks + 1 WHERE usr_id = {user.id}")
        await interaction.send(f"Gave +1 {THANK_TYPE} to {user.mention}")


    @slash_command(description="Posts a random animal image")
    async def animal(self, interaction,
                     animal=SlashOption(description="Choose a type of animal", choices={"Cat", "Dog", "Fox"})):
        args = {"Cat": ("https://api.thecatapi.com/v1/images/search?size=full", "Meow", "https://thecatapi.com", "url"),
                "Dog": ("https://dog.ceo/api/breeds/image/random", "Woof", "https://dog.ceo", "message"),
                "Fox": ("https://randomfox.ca/floof/", "What does the fox say", "https://randomfox.ca", "image")}
        api_url, title, url, json_key = args[animal]
        async with aiohttp.ClientSession() as cs:
            async with cs.get(api_url) as r:
                data = await r.json()
                if type(data) != dict:
                    data = data[0]

                embed = Embed(title=title)
                embed.set_image(url=data[json_key])
                embed.set_footer(text=url)

                await interaction.send(embed=embed)


class BurgerView(ui.View):

    def __init__(self, **params):
        super().__init__(timeout=None)
        self.last_owner_id = params["last_owner_id"]
        self.correct = params["correct"]
        self.attempted = params["attempted"]
        self.ordering = params["ordering"]
        answers = [*params["correct"], *params["wrong"]]
        bot = params["bot"]

        for index in self.ordering:
            self.add_item(self.BurgerButton(label=answers[index], bot=bot))

    class BurgerButton(ui.Button):

        def __init__(self, label, bot):
            super().__init__(style=ButtonStyle.blurple, label=label)
            self.bot = bot


        async def callback(self, interaction):
            if interaction.user.id == self.view.last_owner_id:
                await interaction.send("The burger refuses to be held hostage by you any longer!", ephemeral=True)
                return
            if interaction.user.id in self.view.attempted:
                await interaction.send("You may only attempt to answer once", ephemeral=True)
                return

            if self.label in self.view.correct:
                await interaction.response.defer()
                burgered = uf.get_role(interaction.guild, "Burgered")
                await interaction.user.add_roles(burgered)
                for child in self.view.children:
                    child.disabled = True
                await interaction.edit(view=self.view)
                await interaction.send(f"{interaction.user.mention} has claimed the burger! Now use it wisely.")
                await self.bot.pg_pool.execute((f"DELETE from buttons WHERE channel_id = {interaction.channel.id} "
                                                f"AND message_id = {interaction.message.id}"))

                await db.get_or_insert_usr(self.bot, interaction.user.id, interaction.guild.id)
                await self.bot.pg_pool.execute(f"UPDATE usr SET burgers = burgers + 1 "
                                               f"WHERE usr_id = {interaction.user.id}")

                history = await db.get_note(self.bot, "burger history")
                if history:
                    history = json.loads(history)
                    mentions = [f"<@{user_id}>" for user_id in history]
                    if len(mentions) == 1:
                        msg = f"The last person to hold the burger is {mentions[0]}"
                    else:
                        msg = f"The last people to hold the burger are {','.join(mentions[:-1])} and {mentions[-1]}"
                    await interaction.send(msg, ephemeral=True)
                    history = [interaction.user.id, *history[:4]]
                else:
                    history = [interaction.user.id]
                await self.bot.pg_pool.execute("INSERT INTO tmers (usr_id, expires, ttype) VALUES ($1, $2, $3);",
                                               interaction.user.id, dt.now() + BURGER_TIMEOUT, DB_TMER_BURGER)
                await db.log_or_update_note(self.bot, "burger history", history)

            else:
                await interaction.send(f"{self.label} is not the correct answer - better luck next time!",
                                       ephemeral=True)
                self.view.attempted.append(interaction.user.id)
                await db.update_button_params(self.bot, interaction.message.id, {"attempted": self.view.attempted})


class PredictionView(ui.View):
    def __init__(self, **params):
        super().__init__(timeout=None)
        self.bot = params["bot"]
        self.owner_id = params["owner_id"]
        self.votes_for = params["votes_for"]
        self.votes_against = params["votes_against"]


    @ui.button(emoji="🔮", style=ButtonStyle.blurple)
    async def award_orb(self, button, interaction):
        if interaction.user.id == self.owner_id:
            await interaction.send("You can not award orbs to your own prediction!", ephemeral=True)
            return

        if interaction.user.id in self.votes_for:
            await interaction.send("You have already voted for this prediction!", ephemeral=True)
            return

        if interaction.user.id in self.votes_against:
            self.votes_against.remove(interaction.user.id)

        self.votes_for.append(interaction.user.id)
        await interaction.send("Vote recorded!", ephemeral=True)

        if len(self.votes_for) >= PREDICTION_VOTE_THRESHOLD:
            await interaction.send(f"{uf.id_to_mention(self.owner_id)} has been awarded an orb!")
            await self.bot.pg_pool.execute(f"DELETE FROM buttons WHERE message_id = {interaction.message.id}")
            new_text = re.sub("Does this prediction.*$",
                              f"{uf.id_to_mention(self.owner_id)} was awarded an 🔮 for this prediction!",
                              interaction.message.content)
            await interaction.message.edit(content=new_text, view=None)
        else:
            await db.update_button_params(self.bot, interaction.message.id,
                                          {"votes_for": self.votes_for, "votes_against": self.votes_against})


    @ui.button(emoji="❌", style=ButtonStyle.blurple)
    async def deny_orb(self, button, interaction):
        if interaction.user.id == self.owner_id:
            await self.bot.pg_pool.execute(f"DELETE FROM buttons WHERE message_id = {interaction.message.id}")
            new_text = re.sub("Does this prediction.*$",
                              f"{interaction.user.mention} has marked their prediction as incorrect.",
                              interaction.message.content)
            await interaction.message.edit(content=new_text, view=None)
            return

        if interaction.user.id in self.votes_against:
            await interaction.send("You have already voted against this prediction!", ephemeral=True)
            return

        if interaction.user.id in self.votes_for:
            self.votes_for.remove(interaction.user.id)

        self.votes_against.append(interaction.user.id)
        await interaction.send("Vote recorded!", ephemeral=True)

        if len(self.votes_against) >= PREDICTION_VOTE_THRESHOLD:
            await interaction.send(f"{uf.id_to_mention(self.owner_id)}'s prediction has been deemed unworthy of an 🔮!")
            await self.bot.pg_pool.execute(f"DELETE FROM buttons WHERE message_id = {interaction.message.id}")
            new_text = re.sub("Does this prediction.*$",
                              f"{uf.id_to_mention(self.owner_id)} was not awarded an 🔮 for this prediction!",
                              interaction.message.content)
            await interaction.message.edit(content=new_text, view=None)
        else:
            await db.update_button_params(self.bot, interaction.message.id,
                                          {"votes_for": self.votes_for, "votes_against": self.votes_against})


def setup(bot):
    bot.add_cog(Fun(bot))
