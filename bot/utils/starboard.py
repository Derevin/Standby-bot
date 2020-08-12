import discord
import asyncpg
from db.db_func import ensure_usr_existence
from settings import *

STAR_TRESHOLD = 4


async def get_starboard_msg(bot, msg_id):
    return await bot.pg_pool.fetchrow(
        f"SELECT * FROM starboard WHERE msg_id = {msg_id};"
    )


async def get_starboard_sbid(bot, msg_id):
    return await bot.pg_pool.fetchrow(
        f"SELECT sb_id FROM starboard WHERE msg_id = {msg_id};"
    )


def starboard_embed(message, stars) -> discord.Embed:
    embed = discord.Embed(colour=STARBOARD_COLOUR)
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)
    content_msg = "[Link to message]"
    if len(message.content) > 0:
        content_msg = message.content
        if len(content_msg) > 500:
            content_msg = content_msg[0:500]
            content_msg += " [Click the link to see more]"
    embed.set_thumbnail(url=message.author.avatar_url)
    embed.title = message.author.name
    embed.description = f"[{content_msg}]({message.jump_url})"
    embed.add_field(name="Channel", value=message.channel.mention)
    embed.add_field(name="Stars", value=stars)
    return embed


async def edit_stars(message, stars):
    return await message.edit(
        embed=message.embeds[0].set_field_at(1, name="Stars", value=stars)
    )


async def starboard_handler(bot, payload):
    if isinstance(payload, discord.RawReactionActionEvent):
        if payload.emoji.name == "⭐":
            chnl = bot.get_channel(payload.channel_id)
            msg = await chnl.fetch_message(payload.message_id)
            await ensure_usr_existence(bot, msg.author.id, payload.guild_id)
            stars = 0
            sb_channel = bot.get_channel(STARBOARD_ID)
            for emoji in msg.reactions:
                if emoji.emoji == "⭐":
                    stars = emoji.count

            existcheck = await bot.pg_pool.fetchrow(
                f"SELECT sb_id FROM starboard WHERE msg_id = {payload.message_id};"
            )

            if stars >= STAR_TRESHOLD:  # add to SB
                if existcheck is None:
                    sb_msg = await sb_channel.send(embed=starboard_embed(msg, stars))
                    await bot.pg_pool.execute(
                        "INSERT INTO starboard (msg_id, sb_id, stars, usr_id) VALUES "
                        f"({payload.message_id},{sb_msg.id},{stars},{msg.author.id});"
                    )
                else:
                    sb_msg = await sb_channel.fetch_message(existcheck["sb_id"])
                    await edit_stars(sb_msg, stars)
                    await bot.pg_pool.execute(
                        f"UPDATE starboard SET stars = {stars} WHERE msg_id = {payload.message_id};"
                    )
            else:
                if existcheck is not None:
                    sb_msg = await sb_channel.fetch_message(existcheck["sb_id"])
                    await sb_msg.delete()
                    await bot.pg_pool.execute(
                        f"DELETE FROM starboard WHERE msg_id = {payload.message_id};"
                    )
    elif isinstance(payload, discord.RawReactionClearEvent):
        # if exists in starboard, do something about it, otherwise don't care
        msg = await get_starboard_msg(bot, payload.message_id)
        if msg is not None:
            await msg.delete()
            await bot.pg_pool.execute(
                f"DELETE FROM starboard WHERE msg_id = {payload.message_id};"
            )

    elif isinstance(payload, discord.RawReactionClearEmojiEvent):
        if payload.emoji.name == "⭐":
            # if exists in starboard, do something about it, otherwise don't care
            msg = await get_starboard_msg(bot, payload.message_id)
            if msg is not None:
                await msg.delete()
                await bot.pg_pool.execute(
                    f"DELETE FROM starboard WHERE msg_id = {payload.message_id};"
                )
