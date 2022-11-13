from nextcord.ext import commands, tasks
import nextcord
from nextcord import SlashOption, SelectOption
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

    @nextcord.slash_command(
        description="Commands for setting up and editing the #rules channel",
        default_member_permissions=MODS_ONLY,
    )
    async def rule(self, interaction):
        pass

    @rule.subcommand(description="Add all posts to the rules channel")
    async def create(
        self,
        interaction,
        delay: float = SlashOption(
            description="Delay in seconds between each post", default=0.1
        ),
    ):
        vie = interaction.guild
        rules_ch = get_channel(vie, RULES_CHANNEL_NAME)
        await interaction.send(
            f"Creation process starting in {rules_ch.mention}", ephemeral=True
        )

        await rules_ch.send(GIT_STATIC_URL + "/images/Ginny_Welcome.png")

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
        alli_embed.title = "Step 1 - How did you join us?"
        alli_embed.description = f"""If you're part of a clan in the Warframe alliance, use the 'Warframe' button.
        If you're coming from anywhere else, use the 'Elsewhere' button."""
        view = StepOneView(guild=vie)
        alli_msg = await rules_ch.send(
            "__***Please carefully read the posts below or you will not gain full access to the server***__",
            embed=alli_embed,
            view=view,
        )
        await log_buttons(self.bot, view, rules_ch.id, alli_msg.id)

        await asyncio.sleep(delay)

        clan_embed = nextcord.Embed(color=VIE_PURPLE)

        clan_embed.title = "Step 2 - If you're part of the Warframe alliance, use the menu below to select your clan."
        view = ClanView(guild=vie)
        clan_msg = await rules_ch.send(embed=clan_embed, view=view)
        await log_buttons(self.bot, view, rules_ch.id, clan_msg.id)

        await asyncio.sleep(delay)

        opt_embed = nextcord.Embed(color=VIE_PURPLE)
        opt_embed.title = (
            "Step 3 - Use the menu below if you want to be notified for things like updates, "
            "events and giveaways, or to access certain opt-in channels."
        )
        view = OptInView(guild=vie)
        opt_msg = await rules_ch.send(embed=opt_embed, view=view)
        await log_buttons(self.bot, view, rules_ch.id, opt_msg.id)

        await asyncio.sleep(delay)

        general = get_channel(vie, "general")
        await rules_ch.send(
            "You should now have access to all necessary channels in the server!\n"
            f"Why not pop over to {general.mention} and say hi? You probably have a few welcomes waiting already."
        )

    # @rules.subcommand(description="Add a new role to a post")
    # async def add_role(
    #     self,
    #     interaction,
    #     id=SlashOption(description="ID of the message to add the role to"),
    #     role: nextcord.Role = SlashOption(description="Role to add to the message"),
    #     emoji=SlashOption(
    #         description="Emote to use for the role (default set or from this server only)"
    #     ),
    # ):

    #     rules = get_channel(interaction.guild, RULES_CHANNEL_NAME)
    #     message = await rules.fetch_message(id)
    #     if not message.embeds:
    #         await interaction.send("Cannot add roles to that message", ephemeral=True)
    #         return
    #     new_text = f"React {emoji} for {role.mention}\n"
    #     embed = message.embeds[0]
    #     embed.description += "\n" + new_text
    #     await message.edit(embed=embed)
    #     await message.add_reaction(emoji)
    #     await interaction.send("Role successfully added", ephemeral=True)

    # @rules.subcommand(description="Remove a role from a post")
    # async def remove_role(
    #     self,
    #     interaction,
    #     id=SlashOption(description="ID of the message to remove the role from"),
    #     role: nextcord.Role = SlashOption(
    #         description="Role to remove from the message"
    #     ),
    # ):

    #     rules = get_channel(interaction.guild, RULES_CHANNEL_NAME)
    #     message = await rules.fetch_message(id)
    #     if not message.embeds:
    #         await interaction.send("No roles to remove in that message", ephemeral=True)
    #         return
    #     embed = message.embeds[0]
    #     row = rf"React (.*) for {role.mention}\n?"
    #     match = re.search(row, embed.description)
    #     if not match:
    #         await interaction.send("No such role found in the message", ephemeral=True)
    #     emoji = match.group(1)
    #     embed.description = re.sub(
    #         rf"React .* for {role.mention}\n?", "", embed.description
    #     )
    #     for reaction in message.reactions:
    #         if str(reaction.emoji) == emoji:
    #             await reaction.clear()
    #     await message.edit(embed=embed)
    #     await interaction.send("Role successfully removed", ephemeral=True)

    @rule.subcommand(description="Add a new rule to the post")
    async def add(
        self, interaction, text=SlashOption(description="The text of the rule")
    ):
        rules_ch = get_channel(interaction.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)
        rules = [re.sub(r"^\d+\. ", "", rule) for rule in rules]

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
        await interaction.send("Rule successfully added")

    @rule.subcommand(description="Removes a rule from the post")
    async def remove(
        self,
        interaction,
        number: int = SlashOption(
            description="Number of the rule to remove", min_value=1
        ),
    ):

        rules_ch = get_channel(interaction.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)
        if number > len(rules):
            await interaction.send("No rule with that number.", ephemeral=True)
            return

        rules = [re.sub(r"^\d+\. ", "", rule) for rule in rules]
        rules.pop(number - 1)
        rules = [str(rules.index(rule) + 1) + ". " + rule for rule in rules]
        embed.description = f"\n{EMPTY}\n".join(rules)
        await rules_msg.edit(embed=embed)
        await interaction.send("Rule successfully removed", ephemeral=True)

    @rule.subcommand(description="Edit a rule")
    async def edit(
        self,
        interaction,
        number: int = SlashOption(
            description="Number of the rule to edit", min_value=1
        ),
        new_text=SlashOption(description="New text of the rule"),
    ):

        rules_ch = get_channel(interaction.guild, RULES_CHANNEL_NAME)
        rules_msg = await rules_ch.fetch_message(RULES_MESSAGE_ID)
        embed = rules_msg.embeds[0]
        rules = re.split(rf"\n{EMPTY}\n", embed.description)

        if number > len(rules):
            await interaction.send("No rule with that number", ephemeral=True)

        rules[number - 1] = f"{number}. {new_text}"
        embed.description = f"\n{EMPTY}\n".join(rules)

        await rules_msg.edit(embed=embed)
        await interaction.send("Rule successfully edited", ephemeral=True)

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
                    time = nextcord.utils.utcnow() - member.joined_at
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
                    f"Make sure you read {rules_ch.mention} and use the buttons so you can "
                    "access all of our channels!"
                )


async def leave_message(bot, member):
    if member.guild.id == GUILD_ID:
        channel = nextcord.utils.get(
            member.guild.text_channels, name=ERROR_CHANNEL_NAME
        )
        if channel:
            name = member.name
            time = nextcord.utils.utcnow()
            time = time.strftime("%b %d, %H:%M")
            embed = nextcord.Embed(color=GREY)
            embed.title = "The void grows smaller..."
            embed.set_thumbnail(url=GIT_STATIC_URL + "/images/grave.png")
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
    pass


#     if payload.user_id != BOT_ID and isinstance(
#         payload, nextcord.RawReactionActionEvent
#     ):

#         channel = bot.get_channel(payload.channel_id)
#         message = await channel.fetch_message(payload.message_id)
#         user = await message.guild.fetch_member(payload.user_id)

#         if payload.message_id in ROLE_MESSAGE_IDS:

#             embed = message.embeds[0]

#             match = re.search(
#                 rf"React <?:?{payload.emoji.name}:?\d*>? for <@&(\d*)>",
#                 embed.description,
#             )
#             if match:
#                 role_id = int(match.group(1))
#                 role = nextcord.utils.get(message.guild.roles, id=role_id)
#                 await toggle_role(user, role, payload.event_type)
#             else:
#                 await message.remove_reaction(payload.emoji, user)
#         elif payload.message_id == UNLOCK_MESSAGE_ID:
#             if payload.emoji.name == "Alli":
#                 alliance = get_role(message.guild, "Alliance")
#                 await toggle_role(user, alliance, payload.event_type)
#             elif payload.emoji.name == "BlobWave":
#                 community = get_role(message.guild, "Community")
#                 await toggle_role(user, community, payload.event_type)
#             else:
#                 await message.remove_reaction(payload.emoji, user)


# async def toggle_role(member, role, event_type):
#     if event_type == "REACTION_ADD":
#         await member.add_roles(role)
#     elif event_type == "REACTION_REMOVE":
#         await member.remove_roles(role)


async def level3_handler(before, after):

    if len(after.roles) - len(before.roles) != 1:
        return

    lv3 = get_role(after.guild, "Level 3")
    alliance = get_role(after.guild, "Alliance")

    if lv3 not in before.roles and lv3 in after.roles and alliance in after.roles:
        giveaways = get_role(after.guild, "Giveaways")
        await after.add_roles(giveaways)


class StepOneView(nextcord.ui.View):
    def __init__(self, **params):
        super().__init__(timeout=None)
        guild = params["guild"]
        self.add_item(self.WarframeButton(guild))
        self.add_item(self.CommunityButton(guild))

    class WarframeButton(nextcord.ui.Button):
        def __init__(self, guild):
            super().__init__(
                label="Warframe",
                style=nextcord.ButtonStyle.blurple,
                emoji=get_emoji(guild, "Alli"),
            )

        async def callback(self, interaction):
            alli = get_role(interaction.guild, "Alliance")
            comm = get_role(interaction.guild, "Community")

            await interaction.user.remove_roles(comm)
            await interaction.user.add_roles(alli)

    class CommunityButton(nextcord.ui.Button):
        def __init__(self, guild):
            super().__init__(
                label="Elsewhere",
                style=nextcord.ButtonStyle.blurple,
                emoji=get_emoji(guild, "BlobWave"),
            )

        async def callback(self, interaction):
            await interaction.response.defer()

            alli = get_role(interaction.guild, "Alliance")
            comm = get_role(interaction.guild, "Community")
            await interaction.user.remove_roles(alli)
            await interaction.user.add_roles(comm)

            all_clan_roles = get_roles_by_type(interaction.guild, CLAN_ROLES_DELIMITER)

            await interaction.user.remove_roles(*all_clan_roles)


class ClanView(nextcord.ui.View):
    def __init__(self, **params):
        super().__init__(timeout=None)
        self.choice = None
        guild = params["guild"]
        all_clans = get_roles_by_type(guild, CLAN_ROLES_DELIMITER)
        groups = [
            all_clans[i : i + MAX_MENU_SIZE]
            for i in range(0, len(all_clans), MAX_MENU_SIZE)
        ]
        for group in groups:
            self.add_item(self.ClanSelect(group))
        self.add_item(self.ClanConfirm())

    class ClanSelect(nextcord.ui.Select):
        def __init__(self, clans):
            clans.sort(
                key=lambda clan: (
                    "0"
                    if clan.name in PRIO_ROLES
                    else "1"
                    if clan.name in ROLE_DESCRIPTIONS.keys()
                    else "2"
                )
                + clan.name
            )
            super().__init__(placeholder="Select your clan", min_values=0)
            self.options = [
                SelectOption(
                    label=clan.name,
                    description=ROLE_DESCRIPTIONS[clan.name]
                    if clan.name in ROLE_DESCRIPTIONS
                    else None,
                )
                for clan in clans
            ]

        async def callback(self, interaction):
            self.view.choice = self.values[0] if self.values else None

    class ClanConfirm(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.blurple, label="Choose clan")

        async def callback(self, interaction):

            await interaction.response.defer()
            alli = get_role(interaction.guild, "Alliance")
            if alli not in interaction.user.roles:
                await interaction.send(
                    "Please confirm you're part of the Warframe alliance in Step 1 before choosing a clan",
                    ephemeral=True,
                )
                return
            role = get_role(interaction.guild, self.view.choice)
            all_clan_roles = get_roles_by_type(interaction.guild, CLAN_ROLES_DELIMITER)
            if role:
                await interaction.user.remove_roles(*all_clan_roles)
                await interaction.user.add_roles(role)


class OptInView(nextcord.ui.View):
    def __init__(self, **params):
        guild = params["guild"]
        super().__init__(timeout=None)
        opt_in_roles = get_roles_by_type(guild, OPT_IN_ROLES_DELIMITER)
        groups = [
            opt_in_roles[i : i + MAX_MENU_SIZE]
            for i in range(0, len(opt_in_roles), MAX_MENU_SIZE)
        ]
        self.selected_roles = [[]] * len(groups)
        for index, group in enumerate(groups):
            self.add_item(self.OptInSelect(index, group))

    class OptInSelect(nextcord.ui.Select):
        def __init__(self, index, roles):
            roles.sort(
                key=lambda role: (
                    "0"
                    if role.name in PRIO_ROLES
                    else "1"
                    if role.name in ROLE_DESCRIPTIONS.keys()
                    else "2"
                )
                + role.name
            )
            super().__init__(
                placeholder="Select opt-in roles",
                options=[
                    SelectOption(
                        label=role.name,
                        description=ROLE_DESCRIPTIONS[role.name]
                        if role.name in ROLE_DESCRIPTIONS
                        else None,
                    )
                    for role in roles
                ],
                min_values=0,
                max_values=len(roles),
            )
            self.index = index

        async def callback(self, interaction):
            self.view.selected_roles[self.index] = self.values

    @nextcord.ui.button(
        label="Choose selected roles", style=nextcord.ButtonStyle.blurple, row=4
    )
    async def choose_roles(self, button, interaction):
        for role_list in self.selected_roles:
            for role_name in role_list:
                role = get_role(interaction.guild, role_name)
                if role:
                    await interaction.user.add_roles(role)

    @nextcord.ui.button(
        label="Remove selected roles", style=nextcord.ButtonStyle.red, row=4
    )
    async def remove_roles(self, button, interaction):
        for role_list in self.selected_roles:
            for role_name in role_list:
                role = get_role(interaction.guild, role_name)
                if role:
                    await interaction.user.remove_roles(role)


def setup(bot):
    bot.add_cog(Rules(bot))
