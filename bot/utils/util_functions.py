import asyncio
import datetime
import io
import json
import re
from datetime import datetime as dt, timedelta
from typing import Callable, Union, Sequence, Optional

import nextcord
import requests
from PIL import Image, ImageDraw, ImageFont
from nextcord.ext.tasks import Loop, LF
from nextcord.utils import MISSING

from config.constants import *


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
    match = re.search(r"(\d+)", name)
    if match:
        return nextcord.utils.get(guild.text_channels + guild.threads, id=int(match.group(1)))
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
        users = [user for user in guild.members if (user.name.lower() == query.lower() and user.discriminator == tag)]
    else:
        users = [user for user in guild.members if re.search(query, f"{user.name}|{user.display_name}", re.I)]

    if len(users) == 1:
        return users[0]
    return None


def get_category(guild, name):
    return nextcord.utils.get(guild.categories, name=name)


def int_to_emoji(num):
    emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return emojis[num]


def dynamic_timestamp(time, frmat):
    codes = {"short time": "t", "long time": "T", "short date": "d", "long date": "D", "date and time": "f",
             "date and time with weekday": "F", "relative": "R"}
    mod = codes[frmat] if frmat in codes else frmat if frmat in codes.values() else "f"
    return f"<t:{int(dt.timestamp(time))}:{mod}>"


def int_to_month(num):
    datetime_object = dt.strptime(str(num), "%m")
    return datetime_object.strftime("%B")


def month_to_int(month):
    datetime_object = dt.strptime(month, "%B")
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
        start, stop = [i for i in range(len(guild.roles)) if guild.roles[i].name.lower() == type_.lower()][0:2]
    except ValueError:
        return []
    roles = guild.roles[start + 1: stop]
    roles.sort(key=lambda role: role.name)
    return roles


def id_to_mention(id, id_type="user"):
    id = str(id)

    if id_type == "user":
        return "<@" + id + ">"

    if id_type == "channel":
        return "<#" + id + ">"

    if id_type == "role":
        return "<@&" + id + ">"

    return


def simpsons_error_image(dad, son, text=None, filename="error.png"):
    dad_url = dad.display_avatar.url
    son_url = son.display_avatar.url

    template_url = GIT_STATIC_URL + "/images/simpsons.png"

    template = Image.open(requests.get(template_url, stream=True).raw)

    dad = Image.open(requests.get(dad_url, stream=True).raw).convert("RGBA").resize((300, 300))
    son = Image.open(requests.get(son_url, stream=True).raw).convert("RGBA").resize((225, 225))
    son = son.rotate(-35, expand=True, fillcolor=(255, 255, 255, 0))

    template.paste(dad, (310, 30), dad)
    template.paste(son, (655, 344), son)

    if text:
        text = text.upper()

        draw = ImageDraw.Draw(template)

        font_path = LOCAL_STATIC_PATH / "fonts" / "impact.ttf"
        font = ImageFont.truetype(font=str(font_path), size=40)
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
            for word in re.split(r"(\W+)", text):
                curr_string += word
                curr_width, _ = get_text_dimensions(curr_string, font)
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

    return width, height


async def invoke_slash_command(name, self, *args):
    slash_command = [command for command in self.bot.get_all_application_commands() if command.name == name][0]
    await slash_command.invoke_callback(*args)


def utcnow():
    return nextcord.utils.utcnow()


def now():
    return dt.now(tz=BOT_TZ)


def role_prio(role):
    if role.name in PRIO_ROLES:
        return "0" + role.name
    if role.name in ROLE_DESCRIPTIONS:
        return "1" + role.name
    return "2" + role.name


def message_embed(msg, cmd, trigger_author) -> nextcord.Embed:
    embed_titles = {"copy": "Copied message", "move": "Moved message", "link": "Message preview"}

    trigger_field_titles = {"move": "Moved by", "copy": "Copied by", "link": "Linked by"}

    embed = nextcord.Embed(color=PALE_BLUE)
    embed.title = embed_titles[cmd]
    if msg.author.display_avatar:
        embed.set_thumbnail(url=msg.author.display_avatar.url)
    embed.description = msg.content
    embed.add_field(name="Channel", value=msg.channel.mention)
    timestamp = msg.created_at + timedelta(hours=2)
    if (utcnow() - timestamp).days > 11 * 30:
        timestamp = timestamp.strftime("%b %d, %Y")
    else:
        timestamp = timestamp.strftime("%b %d, %H:%M")
    embed.add_field(name="Sent at", value=timestamp)
    embed.add_field(name=EMPTY, value=EMPTY)
    embed.add_field(name="Original poster", value=msg.author.mention)

    embed.add_field(name=trigger_field_titles[cmd], value=trigger_author.mention)

    if cmd == "copy" or cmd == "link":
        embed.add_field(name="Link to message", value=f"[Click here]({msg.jump_url})")

    if msg.attachments:
        embed.set_image(url=msg.attachments[0].url)
    else:
        link = re.search(r"(https:.*\.(jpe?g|png|gif))", msg.content)
        if link:
            embed.set_image(url=link.group(1))

    return embed


def delayed_loop(*, seconds: float = MISSING, minutes: float = MISSING, hours: float = MISSING,
                 time: Union[datetime.time, Sequence[datetime.time]] = MISSING, count: Optional[int] = None,
                 reconnect: bool = True, loop: asyncio.AbstractEventLoop = MISSING, ) -> Callable[[LF], Loop[LF]]:
    def decorator(func: LF) -> Loop[LF]:
        inner_loop = Loop[LF](func, seconds=seconds, minutes=minutes, hours=hours, time=time, count=count,
                              reconnect=reconnect, loop=loop)


        @inner_loop.before_loop
        async def impr(self):
            await self.bot.wait_until_ready()


        return inner_loop


    return decorator


async def get_user_predictions(bot, user) -> dict:
    query = f"SELECT predictions FROM usr WHERE usr_id = {user.id}"
    recs = await bot.pg_pool.fetch(query)
    predictions = recs[0]["predictions"]
    return json.loads(predictions) if predictions else {}


async def update_user_predictions(bot, user, predictions):
    query = f"UPDATE usr SET predictions = '{json.dumps(predictions)}' WHERE usr_id = {user.id}"
    await bot.pg_pool.execute(query)
