from nextcord import RawReactionActionEvent
from nextcord.ext.commands import Cog

from config.constants import *
from db_integration import db_functions as db
from utils import util_functions as uf


class Reposts(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reposters.start()


    def cog_unload(self):
        self.check_reposters.cancel()


    @Cog.listener()
    async def on_raw_reaction_add(self, payload):

        guild = await self.bot.fetch_guild(GUILD_ID)
        reemoji = uf.get_emoji(guild, REEPOSTER_EMOJI)
        reeposter = uf.get_role(guild, REEPOSTER_NAME)

        if isinstance(payload, RawReactionActionEvent) and payload.emoji == reemoji:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            message_age = uf.utcnow() - message.created_at

            if message_age > REPOSTER_DURATION / 3:
                return

            rees = 0
            for emoji in message.reactions:
                if emoji.emoji == reemoji:
                    rees = emoji.count

            if rees >= REE_THRESHOLD:
                await db.ensure_guild_existence(self.bot, message.guild.id)
                await db.get_or_insert_usr(self.bot, message.author.id, message.guild.id)
                await message.author.add_roles(reeposter)
                exists = await self.bot.pg_pool.fetch("SELECT * FROM tmers "
                                                      f"WHERE ttype={DB_TMER_REPOST} AND usr_id = {message.author.id}")

                if not exists:
                    expires = message.created_at + REPOSTER_DURATION
                    expires = expires.replace(microsecond=0, tzinfo=None)
                    await self.bot.pg_pool.execute("INSERT INTO tmers (usr_id, expires, ttype) VALUES ($1, $2, $3);",
                                                   message.author.id, expires, DB_TMER_REPOST)


    @uf.delayed_loop(seconds=60)
    async def check_reposters(self):
        try:
            gtable = await self.bot.pg_pool.fetch(f"SELECT * FROM tmers WHERE ttype={DB_TMER_REPOST}")
            for rec in gtable:
                timenow = uf.utcnow()
                if timenow.replace(tzinfo=None) <= rec["expires"]:
                    continue

                guild_id = await self.bot.pg_pool.fetchval(f"SELECT guild_id FROM usr WHERE usr_id = {rec['usr_id']}")
                guild = await self.bot.fetch_guild(guild_id)
                user = await guild.fetch_member(rec["usr_id"])
                reeposter = uf.get_role(guild, REEPOSTER_NAME)
                await user.remove_roles(reeposter)
                await self.bot.pg_pool.execute(f"DELETE FROM tmers WHERE tmer_id = {rec['tmer_id']};")
        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception as e:
            await db.log(self.bot, f"Unexpected exception: {e}")
            return


def setup(bot):
    bot.add_cog(Reposts(bot))
