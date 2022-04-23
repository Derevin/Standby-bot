# This example requires the 'message_content' privileged intent to function.

import asyncio
import nextcord
from nextcord.ext import commands, tasks
import youtube_dl
import urllib
import re
from pathlib import Path
from settings import *
import datetime

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    "options": "-vn",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_activity = None
        self.check_voice_activity.start()

    def cog_unload(self):
        self.check_voice_activity.cancel()

    @tasks.loop(minutes=1)
    async def check_voice_activity(self):

        guild = None
        try:
            guild = await self.bot.fetch_guild(GUILD_ID)
        except Exception:
            pass

        if not guild:
            return

        voice_client = nextcord.utils.get(self.bot.voice_clients, guild=guild)

        if not voice_client:
            return

        if voice_client.is_playing():
            self.last_activity = nextcord.utils.utcnow()
        else:
            if self.last_activity and (
                nextcord.utils.utcnow() - self.last_activity
                > datetime.timedelta(minutes=5)
            ):
                await voice_client.disconnect()

    # @commands.command()
    # async def join(self, ctx, *, channel: nextcord.VoiceChannel):
    #     """Joins a voice channel"""

    #     if ctx.voice_client is not None:
    #         return await ctx.voice_client.move_to(channel)

    #     await channel.connect()

    @commands.command()
    @commands.has_any_role(*MOD_ROLES)
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        filepath = str(Path(__file__).parent.parent.parent) + f"/sounds/{query}.mp3"
        source = nextcord.PCMVolumeTransformer(nextcord.FFmpegPCMAudio(filepath))
        ctx.voice_client.play(
            source, after=lambda e: print(f"Player error: {e}") if e else None
        )

        await ctx.send(f"Now playing: {query}")

    # @commands.command()
    # async def yt(self, ctx, *, url):
    #     """Plays from a url (almost anything youtube_dl supports)"""

    #     async with ctx.typing():
    #         player = await YTDLSource.from_url(url, loop=self.bot.loop)
    #         ctx.voice_client.play(
    #             player, after=lambda e: print(f"Player error: {e}") if e else None
    #         )

    #     await ctx.send(f"Now playing: {player.title}")

    @commands.command()
    @commands.has_any_role(*MOD_ROLES)
    async def stream(self, ctx, *, query):

        if not re.search(r"www\.youtube\.com/watch\?v=", query):
            query = best_url(query)

        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: {player.title}")

    # @commands.command()
    # async def volume(self, ctx, volume: int):
    #     """Changes the player's volume"""

    #     if ctx.voice_client is None:
    #         return await ctx.send("Not connected to a voice channel.")

    #     ctx.voice_client.source.volume = volume / 100
    #     await ctx.send(f"Changed volume to {volume}%")

    # @commands.command()
    # async def stop(self, ctx):
    #     """Stops and disconnects the bot from voice"""

    #     await ctx.voice_client.disconnect()

    @play.before_invoke
    # @yt.before_invoke
    @stream.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


def best_url(search):
    search = search.replace(" ", "+")
    html = urllib.request.urlopen(
        "https://www.youtube.com/results?search_query=" + search
    )
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())

    return "https://www.youtube.com/watch?v=" + video_ids[0]


def setup(bot):
    bot.add_cog(Audio(bot))
