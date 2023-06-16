from nextcord.channel import VoiceChannel
from nextcord.ext.commands import Cog

from utils import util_functions as uf


class Voice(Cog):

    def __init__(self, bot):
        self.bot = bot


    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        if before.channel:
            role = uf.get_role(member.guild, before.channel.name)
            if role:
                await member.remove_roles(role)

        if after.channel:
            role = uf.get_role(member.guild, after.channel.name)
            if not role:
                role = await member.guild.create_role(name=after.channel.name, mentionable=True)
            await member.add_roles(role)


    @Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if isinstance(after, VoiceChannel):
            role = uf.get_role(after.guild, before.name)
            if role:
                await role.edit(name=after.name)


    @Cog.listener()
    async def on_guild_channel_delete(self, channel):
        role = uf.get_role(channel.guild, channel.name)
        if role:
            await role.delete()


def setup(bot):
    bot.add_cog(Voice(bot))
