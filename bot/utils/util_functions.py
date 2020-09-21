import discord
import re


def get_emoji(guild, name):
    return discord.utils.get(guild.emojis, name=name)


def get_role(guild, name):
    return discord.utils.get(guild.roles, name=name)


def mention_role(guild, name):
    role = get_role(guild, name)
    if role:
        return role.mention
    else:
        return "@" + name


def get_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)


def get_user(guild, query):

    if re.search(r".*#\d{4}$", query):
        name, tag = re.split(" ?#", query)
        user = discord.utils.get(guild.members, name=name, discriminator=tag)

    else:
        users = [
            user
            for user in guild.members
            if (
                re.search(query, user.display_name, re.I)
                or re.search(query, user.name, re.I)
            )
        ]
        user = users[0] if len(users) == 1 else None

    return user

