import nextcord
from nextcord.ext import commands
import asyncio
from settings import *


def unhandled_error_embed(cont, chan, e) -> nextcord.Embed:
    embed = nextcord.Embed(colour=SOFT_RED)
    embed.add_field(name="Message", value=f"```{cont}```", inline=False)
    embed.add_field(name="Trigger channel", value=chan, inline=False)
    embed.add_field(name="Error", value=str(e), inline=False)
    return embed


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_help_command(self, ctx: commands.Context):
        if ctx.command:
            await ctx.send_help(ctx.command)
        else:
            await ctx.send_help()

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, e: commands.errors.CommandError
    ) -> None:
        if isinstance(e, commands.errors.UserInputError):
            await self.handle_user_input_error(ctx, e)
        elif isinstance(e, commands.errors.CommandNotFound):
            await self._sleep_and_delete(
                await ctx.channel.send(
                    embed=self._get_error_embed(
                        title="Command not found", body=ctx.message.content
                    )
                )
            )
        else:
            if ctx.guild.id == GUILD_ID:
                channel = nextcord.utils.get(
                    ctx.guild.text_channels, name=ERROR_CHANNEL_NAME
                )
                if channel is not None:
                    await channel.send(
                        embed=unhandled_error_embed(ctx.message.content, ctx.channel, e)
                    )

    def _get_error_embed(self, title: str, body: str) -> nextcord.Embed:
        """
        Return an embed that contains the exception.
        credits: https://github.com/python-discord
        """
        return nextcord.Embed(title=title, colour=SOFT_RED, description=body)

    async def _sleep_and_delete(self, msg):
        await asyncio.sleep(20)
        try:
            await msg.delete()
        except Exception:
            print("warn: can't delete msg in _sleep_and_delete")

    async def handle_user_input_error(
        self, ctx: commands.Context, e: commands.errors.UserInputError
    ) -> None:
        """
        Send an error message in `ctx` for UserInputError, sometimes invoking the help command too.
        * MissingRequiredArgument: send an error message with arg name and the help command
        * TooManyArguments: send an error message and the help command
        * BadArgument: send an error message and the help command
        * BadUnionArgument: send an error message including the error produced by the last converter
        * ArgumentParsingError: send an error message
        * Other: send an error message and the help command
        credits: https://github.com/python-discord
        """

        if isinstance(e, commands.errors.MissingRequiredArgument):
            embed = self._get_error_embed("Missing required argument", e.param.name)
            await ctx.send(embed=embed)
            await self.send_help_command(ctx)
        elif isinstance(e, commands.errors.TooManyArguments):
            embed = self._get_error_embed("Too many arguments", str(e))
            await ctx.send(embed=embed)
            await self.send_help_command(ctx)
        elif isinstance(e, commands.errors.BadArgument):
            embed = self._get_error_embed("Bad argument", str(e))
            await ctx.send(embed=embed)
            await self.send_help_command(ctx)
        elif isinstance(e, commands.errors.BadUnionArgument):
            embed = self._get_error_embed("Bad argument", f"{e}\n{e.errors[-1]}")
            await ctx.send(embed=embed)
        elif isinstance(e, commands.errors.ArgumentParsingError):
            embed = self._get_error_embed("Argument parsing error", str(e))
            await ctx.send(embed=embed)
        else:
            embed = self._get_error_embed(
                "Input error",
                "Something about your input seems off. Check the arguments and try again."
                if str(e) == ""
                else str(e),
            )
            await ctx.send(embed=embed)
            if str(e) == "":
                await self.send_help_command(ctx)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
