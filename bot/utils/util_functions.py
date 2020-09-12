import discord


def get_emoji(guild, name):
    emoji = discord.utils.get(guild.emojis, name=name)
    if emoji:
        return emoji
    else:
        return name


def get_role(guild, name):
    role = discord.utils.get(guild.roles, name=name)
    if role:
        return role
    else:
        return None


def mention_role(guild, name):
    role = get_role(guild, name)
    if role:
        return role.mention
    else:
        return "@" + name


def get_channel(guild, name):
    channel = discord.utils.get(guild.text_channels, name=name)
    if channel:
        return channel
    else:
        return None
