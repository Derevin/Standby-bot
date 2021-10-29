from discord.ext import commands, tasks
import discord
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

        if (
            isinstance(payload, discord.RawReactionActionEvent)
            and payload.emoji == reemoji
        ):
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            rees = 0
            for emoji in message.reactions:
                if emoji.emoji == reemoji:
                    rees = emoji.count

            if rees >= 4:

                await ensure_guild_existence(self.bot, message.guild.id)
                await ensure_usr_existence(
                    self.bot, message.author.id, message.guild.id
                )

                params_dict = {
                    "message_id": message.id,
                    "guild_id": guild.id,
                }
                params_json = json.dumps(params_dict)

                await message.author.add_roles(reeposter)

                await self.bot.pg_pool.execute(
                    """INSERT INTO tmers (usr_id, expires, ttype, params) """
                    """VALUES ($1, $2, $3, $4) ON CONFLICT (params) DO NOTHING;""",
                    message.author.id,
                    message.created_at + datetime.timedelta(days=1),
                    DB_TMER_REPOST,
                    params_json,
                )

    @tasks.loop(seconds=60)
    async def check_reposters(self):
        try:
            gtable = await self.bot.pg_pool.fetch("SELECT * FROM tmers")
            for rec in gtable:
                if rec["ttype"] == DB_TMER_REPOST:
                    timenow = datetime.now()
                    if timenow <= rec["expires"]:
                        continue

                    print(f"record expired: {rec}")
                    params_dict = json.loads(rec["params"])
                    if "message_id" not in params_dict or "guild_id" not in params_dict:
                        print("invalid json, deleting")
                        await self.bot.pg_pool.execute(
                            "DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"]
                        )
                        continue

                    guild = self.bot.get_channel(params_dict["guild_id"])

                    user = await guild.fetch_member(rec["usr_id"])

                    reeposter = get_role(guild, REEPOSTER_NAME)

                    await user.remove_roles(reeposter)

                    await self.bot.pg_pool.execute(
                        "DELETE FROM tmers WHERE tmer_id = $1;", rec["tmer_id"]
                    )
                else:
                    print(f"type {rec['ttype']} is not yet implemented")
                    continue
        except AttributeError:  # bot hasn't loaded yet and pg_pool doesn't exist
            return
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return


def setup(bot):
    bot.add_cog(Reposts(bot))
