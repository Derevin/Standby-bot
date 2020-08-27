from discord.ext import commands
import discord
import asyncio
import random
import re
import datetime
import aiohttp
from io import BytesIO
from settings import *
from settings_files.rules_contents import *


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Adds all posts to the rules channel")
    @commands.has_role("Moderator")
    async def create(self, ctx):
        await ctx.invoke(self.bot.get_command("clear"), amount=15)

        delay = 0.1
        vie = ctx.guild
        rules_ch = get_channel(vie, RULES_CHANNEL_NAME)
        await rules_ch.send(
            "https://cdn.discordapp.com/attachments/744224801429782679/748495451744894976/Ginny_Welcome.png"
        )
        await asyncio.sleep(delay)
        rules_embed = discord.Embed(color=VIE_PURPLE)
        rules_embed.title = r"__RULES__"
        rules_embed.description = f"\n{EMPTY}\n".join(RULES_LIST)
        rules_embed.description
        await rules_ch.send(embed=rules_embed)
        info_embed = discord.Embed(color=VIE_PURPLE)
        info_embed.title = r"__GENERAL INFO__"
        info_embed.description = GENERAL_INFO
        await rules_ch.send(embed=info_embed)
        await asyncio.sleep(delay)

        alli_embed = discord.Embed(color=VIE_PURPLE)
        alli_embed.title = "Step 1 - React to this post"
        alli_embed.description = f"""If you're part of a clan in the Warframe alliance, react with {get_emoji(vie,'Alli')}.
        If you're coming from anywhere else, react with 🤠."""
        alli_msg = await rules_ch.send(
            "__***Please carefully read the posts below or you will not gain full access to the server***__",
            embed=alli_embed,
        )
        await alli_msg.add_reaction(get_emoji(vie, "Alli"))
        await alli_msg.add_reaction("🤠")
        await asyncio.sleep(delay)

        clan_embed = discord.Embed(color=VIE_PURPLE)

        clan_embed.title = "Step 2 - If you're part of the Warframe alliance, react to this post with your clan's emoji"
        clan_desc = ""
        for clan in CLANS_PART_1:
            clan_desc += f"React {get_emoji(vie,CLANS_PART_1[clan])} for {mention_role(vie,clan)}\n"
        clan_embed.description = clan_desc
        clan_msg = await rules_ch.send(embed=clan_embed)
        for clan in CLANS_PART_1:
            await clan_msg.add_reaction(get_emoji(vie, CLANS_PART_1[clan]))

        clan_embed = discord.Embed(color=VIE_PURPLE)

        clan_desc = ""
        for clan in CLANS_PART_2:
            clan_desc += f"React {get_emoji(vie,CLANS_PART_2[clan])} for {mention_role(vie,clan)}\n"
        clan_embed.description = clan_desc
        clan_msg = await rules_ch.send(embed=clan_embed)
        for clan in CLANS_PART_2:
            await clan_msg.add_reaction(get_emoji(vie, CLANS_PART_2[clan]))

        await asyncio.sleep(delay)

        opt_embed = discord.Embed(color=VIE_PURPLE)
        opt_embed.title = (
            "Step 3 - If you want to be notified for things like updates, events and giveaways,"
            " or to access certain opt-in channels, react to this post"
        )

        offers_channel = get_channel(vie, "offers")
        opt_embed.description = (
            f"React ⬆️ for {mention_role(vie,'UpdateSquad')} and be notified about alliance "
            f"and server changes, giveaways, events, polls etc.\n"
            f"React 💰 for {mention_role(vie,'Offers')} for news about free or"
            f" discounted games in {offers_channel.mention}\n{EMPTY}\n"
        )

        for role in OPT_IN_ROLES:
            opt_embed.description += f"React {get_emoji(vie, OPT_IN_ROLES[role])} for {mention_role(vie, role)}\n"
        opt_msg = await rules_ch.send(embed=opt_embed)
        await opt_msg.add_reaction("⬆️")
        await opt_msg.add_reaction("💰")
        for role in OPT_IN_ROLES:
            await opt_msg.add_reaction(get_emoji(vie, OPT_IN_ROLES[role]))
        await asyncio.sleep(delay)

        general = get_channel(vie, "general")
        await rules_ch.send(
            "You should now have access to all necessary channels in the server!\n"
            f"Why not pop over to {general.mention} and say hi? You probably have a few welcomes waiting already."
        )

    @commands.command(brief="Adds a new role to a post")
    @commands.has_role("Moderator")
    async def addrole(self, ctx, msg_id, emoji, role):

        rules = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        message = await rules.fetch_message(msg_id)
        if not message.embeds:
            raise commands.errors.BadArgument("Cannot add roles to that message")
        new_text = f"React {emoji} for {role}\n"
        embed = message.embeds[0]
        embed.description += "\n" + new_text
        await message.edit(embed=embed)
        await message.add_reaction(emoji)

    @commands.command(brief="Removes a role from a post")
    @commands.has_role("Moderator")
    async def removerole(self, ctx, msg_id, role):

        rules = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        message = await rules.fetch_message(msg_id)
        if not message.embeds:
            raise commands.errors.BadArgument("No roles to remove in that message")
        embed = message.embeds[0]
        row = rf"React (.*) for {role}\n?"
        match = re.search(row, embed.description)
        if not match:
            raise commands.errors.BadArgument("No such role found in the message")
        emoji = match.group(1)
        embed.description = re.sub(rf"React .* for {role}\n?", "", embed.description)
        for reaction in message.reactions:
            if str(reaction.emoji) == emoji:
                await reaction.clear()
        await message.edit(embed=embed)

    @commands.command(brief="Adds a new rule to the post")
    @commands.has_role("Moderator")
    async def addrule(self, ctx, *text):
        rules_ch = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)
        rules = [re.sub(r"^\d+\. ", "", rule) for rule in rules]

        if not text:
            raise commands.errors.UserInputError("Please enter the rule text")

        if re.match(r"^\d+$", text[-1]):
            text, number = " ".join(text[:-1]), int(text[-1])
            if number > len(rules) + 1 or number < 1:
                number = len(rules) + 1
        else:
            text, number = " ".join(text), len(rules) + 1

        rules.insert(number - 1, text)
        rules = [str(rules.index(rule) + 1) + ". " + rule for rule in rules]
        embed.description = f"\n{EMPTY}\n".join(rules)
        await rules_msg.edit(embed=embed)

    @commands.command(brief="Removes a rule from the post")
    @commands.has_role("Moderator")
    async def removerule(self, ctx, number):
        try:
            number = int(number)
        except Exception:
            raise commands.errors.BadArgument("Please enter a rule number to remove.")

        rules_ch = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)
        if number > len(rules) or number < 1:
            raise commands.errors.BadArgument("No rule with that number.")

        rules = [re.sub(r"^\d+\. ", "", rule) for rule in rules]
        rules.pop(number - 1)
        rules = [str(rules.index(rule) + 1) + ". " + rule for rule in rules]
        embed.description = f"\n{EMPTY}\n".join(rules)
        await rules_msg.edit(embed=embed)

    @commands.command(brief="Edits a rule")
    @commands.has_role("Moderator")
    async def editrule(self, ctx, number, *text):
        try:
            number = int(number)
        except Exception:
            raise commands.errors.BadArgument("Please enter a rule number to remove.")

        if not text:
            raise commands.errors.UserInputError("Please enter the rule text")

        text = " ".join(text)

        rules_ch = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)

        if number > len(rules) or number < 1:
            raise commands.errors.BadArgument("No rule with that number.")

        rules[number - 1] = f"{number}. {text}"
        embed.description = f"\n{EMPTY}\n".join(rules)

        await rules_msg.edit(embed=embed)


async def role_handler(bot, payload):
    if payload.user_id != BOT_ID and isinstance(
        payload, discord.RawReactionActionEvent
    ):

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        embed = message.embeds[0]
        user = message.guild.get_member(payload.user_id)

        if payload.message_id in ROLE_MESSAGE_IDS:

            match = re.search(
                rf"React <?:?{payload.emoji.name}:?\d*>? for <@&(\d*)>",
                embed.description,
            )
            if match:
                role_id = int(match.group(1))
                role = discord.utils.get(message.guild.roles, id=role_id)
                await toggle_role(user, role, payload.event_type)
            else:
                await message.remove_reaction(payload.emoji, user)
        elif payload.message_id == UNLOCK_MESSAGE_ID:
            if payload.emoji.name == "Alli":
                alliance = get_role(message.guild, "Alliance")
                await toggle_role(user, alliance, payload.event_type)
            elif payload.emoji.name == "🤠":
                guest = get_role(message.guild, "Guest")
                await toggle_role(user, guest, payload.event_type)
            else:
                await message.remove_reaction(payload.emoji, user)


async def toggle_role(member, role, event_type):
    if event_type == "REACTION_ADD":
        await member.add_roles(role)
    elif event_type == "REACTION_REMOVE":
        await member.remove_roles(role)


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


def setup(bot):
    bot.add_cog(Rules(bot))
