import nextcord
import re
import datetime
from pathlib import Path
import io
from PIL import Image, ImageDraw, ImageFont
import requests
import json
from settings import *


def get_emoji(guild, name):
    return nextcord.utils.get(guild.emojis, name=name)


def get_role(guild, name):
    return nextcord.utils.find(lambda r: r.name.lower() == name.lower(), guild.roles)


def mention_role(guild, name):
    role = get_role(guild, name)
    if role:
        return role.mention
    else:
        return "@" + name


def get_channel(guild, name):
    match = re.search(r"^<#(\d+)>$", name)
    if match:
        return nextcord.utils.get(
            guild.text_channels + guild.threads, id=int(match.group(1))
        )
    else:
        name = name.replace("#", "")
        channel = nextcord.utils.get(guild.text_channels, name=name)
        return channel if channel else nextcord.utils.get(guild.threads, name=name)


def get_user(guild, query):
    if re.search(r".*#\d{4}$", query):
        query, tag = re.split(" ?#", query)
    else:
        tag = None

    if tag:
        users = [
            user
            for user in guild.members
            if (user.name.lower() == query.lower() and user.discriminator == tag)
        ]

    else:
        users = [
            user
            for user in guild.members
            if (
                re.search(query, user.display_name, re.I)
                or re.search(query, user.name, re.I)
            )
        ]

    if len(users) == 1:
        return users[0]
    return None


def int_to_emoji(num):
    emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return emojis[num]


def dynamic_timestamp(time, frmat):
    mod = "t" if frmat == "short" else "R" if frmat == "delta" else "f"
    return f"<t:{int(datetime.datetime.timestamp(time))}:{mod}>"


def int_to_month(num):
    datetime_object = datetime.datetime.strptime(str(num), "%m")
    return datetime_object.strftime("%B")


def month_to_int(month):
    datetime_object = datetime.datetime.strptime(month, "%B")
    return datetime_object.month


def get_mentioned_ids(text):
    raw_ids = re.findall(r"<\D*\d+>", text)
    ids = [int(re.sub(r"\D", "", id)) for id in raw_ids]
    return ids


async def get_mentioned_users(text, guild):
    ids = get_mentioned_ids(text)
    users = [await guild.fetch_member(id) for id in ids]
    return users


def get_roles_by_type(guild, type_):
    try:
        start, stop = [
            i
            for i in range(len(guild.roles))
            if guild.roles[i].name.lower() == type_.lower()
        ][0:2]
    except ValueError:
        return []
    roles = guild.roles[start + 1 : stop]
    roles.sort(key=lambda role: role.name)
    return roles


def get_local_static_path():
    return str(Path(__file__).parent.parent.parent) + "/static"


def id_to_mention(id, id_type="user"):
    id = str(id)

    if id_type == "user":
        return "<@" + id + ">"

    if id_type == "channel":
        return "<#" + id + ">"

    if id_type == "role":
        return "<@&" + id + ">"

    return


async def log_buttons(bot, view, channel_id, message_id, params=None):
    view_type = view.__class__.__module__ + " " + view.__class__.__name__
    await bot.pg_pool.execute(
        """INSERT INTO buttons (type, channel_id, message_id, params) """
        """VALUES ($1, $2, $3, $4);""",
        view_type,
        channel_id,
        message_id,
        json.dumps(params) if params else None,
    )


def simpsons_error_image(dad, son, text=None, filename="error.png"):
    dad_url = dad.display_avatar.url
    son_url = son.display_avatar.url

    template_url = GIT_STATIC_URL + "/images/simpsons.png"

    template = Image.open(requests.get(template_url, stream=True).raw)

    dad = (
        Image.open(requests.get(dad_url, stream=True).raw)
        .convert("RGBA")
        .resize((300, 300))
    )
    son = (
        Image.open(requests.get(son_url, stream=True).raw)
        .convert("RGBA")
        .resize((225, 225))
        .rotate(-35, expand=True, fillcolor=(255, 255, 255, 0))
    )

    template.paste(dad, (310, 30), dad)
    template.paste(son, (655, 344), son)

    if text:
        text = text.upper()

        draw = ImageDraw.Draw(template)

        font_path = get_local_static_path() + "/fonts/impact.ttf"
        font = ImageFont.truetype(font=font_path, size=40)
        width, height = get_text_dimensions(text, font)

        if width <= 370:
            x_coord = 565
            y_coord = 280

            draw.text((x_coord - 3, y_coord - 3), text, (0, 0, 0), font=font)
            draw.text((x_coord + 3, y_coord - 3), text, (0, 0, 0), font=font)
            draw.text((x_coord + 3, y_coord + 3), text, (0, 0, 0), font=font)
            draw.text((x_coord - 3, y_coord + 3), text, (0, 0, 0), font=font)
            draw.text((x_coord, y_coord), text, (255, 255, 255), font=font)

        else:
            rows = []
            num_rows = width // 280 + 1
            row_width = width / num_rows
            curr_string = ""
            curr_width = 0
            for word in re.split(r"(\W+)", text):
                curr_string += word
                curr_width, _ = get_text_dimensions(curr_string, font)
                # print(f"{curr_string} is {curr_width}")
                if curr_width >= row_width:
                    rows.append(curr_string)
                    curr_string = ""

            if curr_string:
                rows.append(curr_string)

            x_coord = 615
            y_coord = 280

            for row in reversed(rows):
                draw.text((x_coord - 3, y_coord - 3), row, (0, 0, 0), font=font)
                draw.text((x_coord + 3, y_coord - 3), row, (0, 0, 0), font=font)
                draw.text((x_coord + 3, y_coord + 3), row, (0, 0, 0), font=font)
                draw.text((x_coord - 3, y_coord + 3), row, (0, 0, 0), font=font)
                draw.text((x_coord, y_coord), row, (255, 255, 255), font=font)

                y_coord -= height + 5

    obj = io.BytesIO()
    template.save(obj, "png")
    obj.seek(0)
    return nextcord.File(obj, filename=filename)


def get_text_dimensions(text, font):
    ascent, descent = font.getmetrics()

    width = font.getmask(text).getbbox()[2]
    height = font.getmask(text).getbbox()[3] + descent

    return (width, height)


async def get_db_note(bot, key):
    notes = await bot.pg_pool.fetch(f"SELECT * FROM notes WHERE key = '{key}'")
    return notes[0]["value"] if notes else ""


async def log_or_update_db_note(bot, key, value):
    note = await get_db_note(bot, key)
    if note:
        await bot.pg_pool.execute(
            f"UPDATE notes SET value = '{value}' where key = '{key}'"
        )
    else:
        await bot.pg_pool.execute(
            f"INSERT INTO notes (key,  value) VALUES ('{key}', '{value}')"
        )


def get_tweet_data(tweet_id):
    request_url = (
        f"https://api.twitter.com/2/tweets/{tweet_id}?tweet.fields=attachments"
    )
    tweet = requests.request(
        "GET",
        request_url,
        headers={
            "Authorization": "Bearer " + TWITTER_BEARER_TOKEN,
            "User-Agent": "v2TweetLookupPython",
        },
    )
    tweet_dict = json.loads(tweet.content.decode("utf-8"))
    return tweet_dict["data"] if "data" in tweet_dict else {}


async def invoke_slash_command(name, self, *args):
    slash_command = [
        command
        for command in self.bot.get_all_application_commands()
        if command.name == name
    ][0]
    await slash_command.invoke_callback(*args)
