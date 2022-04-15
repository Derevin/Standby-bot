from nextcord.ext import commands, tasks
import nextcord
import asyncio
import random
import re
import datetime
import aiohttp
from io import BytesIO
from settings import *
from settings_files.rules_contents import *
from cogs.tickets import CLAIMABLE_CHANNEL_NAME
from utils.util_functions import *


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kick_inactives.start()

    def cog_unload(self):
        self.kick_inactives.cancel()

    @commands.command(brief="Adds all posts to the rules channel")
    @commands.has_role("Moderator")
    async def create(self, ctx, delay=0.1):

        await ctx.message.delete()
        vie = ctx.guild
        rules_ch = get_channel(vie, RULES_CHANNEL_NAME)
        await rules_ch.send(
            "https://cdn.discordapp.com/attachments/744224801429782679/748495451744894976/Ginny_Welcome.png"
        )
        await asyncio.sleep(delay)
        rules_embed = nextcord.Embed(color=VIE_PURPLE)
        rules_embed.title = r"__RULES__"
        rules_embed.description = f"\n{EMPTY}\n".join(RULES_LIST)
        rules_embed.description
        await rules_ch.send(embed=rules_embed)
        info_embed = nextcord.Embed(color=VIE_PURPLE)
        info_embed.title = r"__GENERAL INFO__"
        info_embed.description = GENERAL_INFO
        await rules_ch.send(embed=info_embed)
        await asyncio.sleep(delay)

        alli_embed = nextcord.Embed(color=VIE_PURPLE)
        alli_embed.title = "Step 1 - React to this post"
        alli_embed.description = f"""If you're part of a clan in the Warframe alliance, react with {get_emoji(vie,'Alli')}.
        If you're coming from anywhere else, react with {get_emoji(vie,'BlobWave')}."""
        alli_msg = await rules_ch.send(
            "__***Please carefully read the posts below or you will not gain full access to the server***__",
            embed=alli_embed,
        )
        await alli_msg.add_reaction(get_emoji(vie, "Alli"))
        await alli_msg.add_reaction(get_emoji(vie, "BlobWave"))
        await asyncio.sleep(delay)

        clan_embed = nextcord.Embed(color=VIE_PURPLE)

        clan_embed.title = "Step 2 - If you're part of the Warframe alliance, react to this post with your clan's emoji"
        clan_desc = ""
        for clan in CLANS_PART_1:
            clan_desc += f"React {get_emoji(vie,CLANS_PART_1[clan])} for {mention_role(vie,clan)}\n"
        clan_embed.description = clan_desc
        clan_msg = await rules_ch.send(embed=clan_embed)
        for clan in CLANS_PART_1:
            await clan_msg.add_reaction(get_emoji(vie, CLANS_PART_1[clan]))

        clan_embed = nextcord.Embed(color=VIE_PURPLE)

        clan_desc = ""
        for clan in CLANS_PART_2:
            clan_desc += f"React {get_emoji(vie,CLANS_PART_2[clan])} for {mention_role(vie,clan)}\n"
        clan_embed.description = clan_desc
        clan_msg = await rules_ch.send(embed=clan_embed)
        for clan in CLANS_PART_2:
            await clan_msg.add_reaction(get_emoji(vie, CLANS_PART_2[clan]))

        await asyncio.sleep(delay)

        opt_embed = nextcord.Embed(color=VIE_PURPLE)
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
    async def addrole(self, ctx, msg_id, role, emoji):

        rules = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        message = await rules.fetch_message(msg_id)
        if not message.embeds:
            raise commands.errors.BadArgument("Cannot add roles to that message")
        if role not in [guild_role.mention for guild_role in ctx.guild.roles]:
            raise commands.errors.BadArgument("No role with that name found.")
        new_text = f"React {emoji} for {role}\n"
        embed = message.embeds[0]
        embed.description += "\n" + new_text
        await message.edit(embed=embed)
        await message.add_reaction(emoji)
        await ctx.message.delete()

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
        await ctx.message.delete()

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
        await ctx.message.delete()

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
        await ctx.message.delete()

    @commands.command(brief="Edits a rule")
    @commands.has_role("Moderator")
    async def editrule(self, ctx, number, *, text):
        try:
            number = int(number)
        except Exception:
            raise commands.errors.BadArgument("Please enter a rule number to remove.")

        if not text:
            raise commands.errors.UserInputError("Please enter the rule text")

        rules_ch = get_channel(ctx.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)

        if number > len(rules) or number < 1:
            raise commands.errors.BadArgument("No rule with that number.")

        rules[number - 1] = f"{number}. {text}"
        embed.description = f"\n{EMPTY}\n".join(rules)

        await rules_msg.edit(embed=embed)
        if not ctx.message.embeds:
            await ctx.message.delete()

    @tasks.loop(hours=8)
    async def kick_inactives(self):
        guild = None

        try:
            guild = await self.bot.fetch_guild(GUILD_ID)
        except Exception:
            pass

        if guild:
            async for member in guild.fetch_members():
                if (
                    not member.bot
                    and get_role(member.guild, "Alliance") not in member.roles
                    and get_role(member.guild, "Community") not in member.roles
                ):
                    time = datetime.datetime.utcnow() - member.joined_at
                    if time.days >= 30:
                        try:
                            await member.send(
                                "Hi! You have been automatically kicked from the Vie for the Void Discord "
                                f"as you have failed to read our rules and"
                                " unlock the full server within 30 days. If this "
                                f"was an accident, please feel free to join us again!\n{EMPTY}\n{INVITE_LINK}"
                            )
                        except Exception:
                            pass
                        try:
                            maint = await self.bot.fetch_channel(ERROR_CHANNEL_ID)
                            await maint.send(
                                f"{member.name}#{member.discriminator} has been kicked due to inactivity."
                            )
                        except Exception:
                            pass

                        try:
                            await member.kick()
                        except Exception as e:
                            print(
                                f"{member.name}#{member.discriminator} couldn't be kicked:\n{e}"
                            )


async def welcome_message(bot, member):
    if member.guild.id == GUILD_ID:
        general = nextcord.utils.get(member.guild.text_channels, name="general")
        rules_ch = nextcord.utils.get(member.guild.text_channels, name="rules")
        rules_text = rules_ch.mention if rules_ch else "rules"
        if general:
            message = (
                f"Welcome {member.mention}!\n"
                "Wondering why the server seems so void of channels?\n"
                f"Please read the {rules_text} to unlock the full server!\n"
                "https://www.youtube.com/watch?v=67h8GyNgEmA"
            )
            await general.send(message)
            await asyncio.sleep(30 * 60)
            if (
                not member.bot
                and member.guild.get_member(member.id)
                and get_role(member.guild, "Alliance") not in member.roles
                and get_role(member.guild, "Community") not in member.roles
            ):
                await general.send(
                    f"Hey {member.mention} - I see you still haven't unlocked the full server. "
                    f"Make sure you read {rules_ch.mention} and react to the post so you can "
                    "access all of our channels!"
                )


async def leave_message(bot, member):
    if member.guild.id == GUILD_ID:
        channel = nextcord.utils.get(
            member.guild.text_channels, name=ERROR_CHANNEL_NAME
        )
        if channel:
            name = member.name
            time = datetime.datetime.utcnow()
            time = time.strftime("%b %d, %H:%M")
            embed = nextcord.Embed(color=GREY)
            embed.title = "The void grows smaller..."
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/744224801429782679/747945281248559184/grave.png"
            )
            embed.description = f":rocket: {name} has left the void :rocket:"
            causes = [
                "ded",
                "Couldn't find their socks fast enough",
                "Yeeted themselves off a very high chair",
                "Forgot how to breathe",
                "Stickbugged one time too many",
                "Disrespected the pedestal",
                "Terminal case of being horny",
                "Sacrificed at the altar of Tzeentch",
                "Critical paper cut",
                "Executed by the ICC for their numerous war crimes in Albania",
            ]
            animu = nextcord.utils.get(member.guild.text_channels, name="animu")
            if animu:
                causes.append(f"Too much time spent in {animu.mention}")
            embed.add_field(name="Time of death", value=time)
            embed.add_field(
                name="Cause of death", value=causes[random.randint(1, len(causes)) - 1]
            )
            await channel.send(embed=embed)


async def role_handler(bot, payload):
    if payload.user_id != BOT_ID and isinstance(
        payload, nextcord.RawReactionActionEvent
    ):

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = await message.guild.fetch_member(payload.user_id)

        if payload.message_id in ROLE_MESSAGE_IDS:

            embed = message.embeds[0]

            match = re.search(
                rf"React <?:?{payload.emoji.name}:?\d*>? for <@&(\d*)>",
                embed.description,
            )
            if match:
                role_id = int(match.group(1))
                role = nextcord.utils.get(message.guild.roles, id=role_id)
                await toggle_role(user, role, payload.event_type)
            else:
                await message.remove_reaction(payload.emoji, user)
        elif payload.message_id == UNLOCK_MESSAGE_ID:
            if payload.emoji.name == "Alli":
                alliance = get_role(message.guild, "Alliance")
                await toggle_role(user, alliance, payload.event_type)
            elif payload.emoji.name == "BlobWave":
                community = get_role(message.guild, "Community")
                await toggle_role(user, community, payload.event_type)
            else:
                await message.remove_reaction(payload.emoji, user)


async def toggle_role(member, role, event_type):
    if event_type == "REACTION_ADD":
        await member.add_roles(role)
    elif event_type == "REACTION_REMOVE":
        await member.remove_roles(role)


async def level3_handler(before, after):

    if len(after.roles) - len(before.roles) != 1:
        return

    lv3 = get_role(after.guild, "Level 3")
    alliance = get_role(after.guild, "Alliance")

    if lv3 not in before.roles and lv3 in after.roles and alliance in after.roles:
        giveaways = get_role(after.guild, "Giveaways")
        await after.add_roles(giveaways)


def setup(bot):
    bot.add_cog(Rules(bot))
