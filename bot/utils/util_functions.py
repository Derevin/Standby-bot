import discord
import re


def get_emoji(guild, name):
    return discord.utils.get(guild.emojis, name=name)


def get_role(guild, name):
    return discord.utils.find(lambda r: r.name.lower() == name.lower(), guild.roles)


def mention_role(guild, name):
    role = get_role(guild, name)
    if role:
        return role.mention
    else:
        return "@" + name


def get_channel(guild, name):
    match = re.search(r"^<#(\d+)>$", name)
    if match:
        return discord.utils.get(guild.text_channels, id=int(match.group(1)))
    else:
        return discord.utils.get(guild.text_channels, name=name)


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
