import nextcord
import re
import datetime
from pathlib import Path


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


def get_vanity_roles(guild):
    start, stop = [
        i for i in range(len(guild.roles)) if guild.roles[i].name == "Vanity"
    ][0:2]
    vanity_roles = guild.roles[start + 1 : stop]
    vanity_roles.sort(key=lambda role: role.name)
    return vanity_roles


def get_local_static_path():
    return str(Path(__file__).parent.parent.parent) + "/static"
