from nextcord.ext import commands, tasks
import nextcord
import datetime
from settings import *
from utils.util_functions import *
import json
from db.db_func import ensure_guild_existence, ensure_usr_existence
import sys
import traceback


class Reposts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reposters.start()

    def cog_unload(self):
        self.check_reposters.cancel()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        guild = await self.bot.fetch_guild(GUILD_ID)
        reemoji = get_emoji(guild, REEPOSTER_EMOJI)
        reeposter = get_role(guild, REEPOSTER_NAME)
        reposter_duration = datetime.timedelta(days=1)
        ree_threshold = 4

        if (
            isinstance(payload, nextcord.RawReactionActionEvent)
            and payload.emoji == reemoji
        ):
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            message_age = nextcord.utils.utcnow() - message.created_at

            if message_age > reposter_duration / 3:
                return

            rees = 0
            for emoji in message.reactions:
                if emoji.emoji == reemoji:
                    rees = emoji.count

            if rees >= ree_threshold:

                await ensure_guild_existence(self.bot, message.guild.id)
                await ensure_usr_existence(
                    self.bot, message.author.id, message.guild.id
                )
                await message.author.add_roles(reeposter)

                exists = await self.bot.pg_pool.fetch(
                    f"SELECT * FROM tmers WHERE ttype={DB_TMER_REPOST} AND usr_id = {message.author.id}"
                )

                if not exists:
                    expires = message.created_at + reposter_duration

                    expires = expires.replace(microsecond=0, tzinfo=None)

                    await self.bot.pg_pool.execute(
                        """INSERT INTO tmers (usr_id, expires, ttype) """
                        """VALUES ($1, $2, $3);""",
                        message.author.id,
                        expires,
                        DB_TMER_REPOST,
                    )

    @tasks.loop(seconds=60)
    async def check_reposters(self):
        try:
            gtable = await self.bot.pg_pool.fetch(
                f"SELECT * FROM tmers WHERE ttype={DB_TMER_REPOST}"
            )
            for rec in gtable:

                timenow = nextcord.utils.utcnow()

                if timenow.replace(tzinfo=None) <= rec["expires"]:
                    continue

                print(f"record expired: {rec}")

                guild_id = await self.bot.pg_pool.fetchval(
                    f"SELECT guild_id FROM usr WHERE usr_id = {rec['usr_id']}"
                )

                guild = await self.bot.fetch_guild(guild_id)

                user = await guild.fetch_member(rec["usr_id"])

                reeposter = get_role(guild, REEPOSTER_NAME)

                await user.remove_roles(reeposter)

                await self.bot.pg_pool.execute(
                    "DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"]
                )
        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return


def setup(bot):
    bot.add_cog(Reposts(bot))
