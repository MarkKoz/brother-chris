import re
import traceback
from typing import Pattern

import discord
from discord.ext import commands

from brotherchris import logger
from brotherchris.cogs import utils

# Loads the configuration file.
config: dict = utils.load_config("Bot")
name: str = config["name"]

bot: commands.Bot = commands.Bot(
    command_prefix=config["prefixes"],
    description=name,
    pm_help=None,
    help_attrs=dict(hidden=True))


@bot.event
async def on_ready():
    """
    Called when the :class:`client<discord.Client>` is done preparing the data
    received from Discord. Usually after login is successful and the
    Client.servers and co. are filled up.

    Note
    -------
    This function is not guaranteed to be the first event called. Likewise, this
    function is not guaranteed to only be called once. This library implements
    reconnection logic and thus will end up calling this event whenever a RESUME
    request fails.

    Returns
    -------
    None
    """
    log.info(f"{name} logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_resumed():
    """
    Called when the :class:`client<discord.Client>` has resumed a session.

    Returns
    -------
    None
    """
    log.info(f"{name} resumed.")


@bot.event
async def on_message(msg: discord.Message):
    """
    Called when a :class:`message<discord.Message>` is created and sent to a
    server.

    Parameters
    ----------
    msg: discord.Message
        The message the creation of which called this event.

    Returns
    -------
    None
    """
    if not msg.author.bot:
        await bot.process_commands(msg)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """
    An error handler that is called when an error is raised inside a command.

    Parameters
    ----------
    ctx: commands.Context
        The context in which the command was invoked.
    error: commands.CommandError
        The error that was raised.

    Returns
    -------
    None
    """
    # Skips errors that were already handled locally.
    if getattr(ctx, "handled", False):
        return

    if isinstance(error, commands.NoPrivateMessage):
        await ctx.author.send("This command cannot be used in direct messages.")
    elif isinstance(error, commands.TooManyArguments):
        await ctx.message.channel.send("Too many arguments.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.channel.send(
            f"Missing required argument `{error.param.name}`.")
    elif isinstance(error, commands.NotOwner) or \
            isinstance(error, commands.MissingPermissions):
        await ctx.message.channel.send(
            "You do not have the required permissions to invoke this "
            "command.")
    elif isinstance(error, commands.CommandOnCooldown) or \
            isinstance(error, commands.CheckFailure):
        await ctx.message.channel.send(error)
    elif isinstance(error, commands.DisabledCommand):
        await ctx.message.channel.send(
            f"This command is currently disabled and cannot be used.")
    elif isinstance(error, commands.BadArgument):
        await ctx.message.channel.send(f"Bad argument: {error}")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.message.channel.send(
            "Oops! The bot does not have the required permissions to "
            "execute this command.")
        log.error(
            f"{ctx.command.qualified_name} cannot be executed because the bot "
            f"is missing the following permissions: {', '.join(error.list)}")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.message.channel.send("Something went wrong internally!")
        log.error(
            f"{ctx.command.qualified_name} failed to execute. "
            f"{error.original.__class__.__name__}: {error.original}\n"
            f"{''.join(traceback.format_tb(error.original.__traceback__))}")


@bot.check
async def global_user_check(ctx: commands.Context) -> bool:
    """
    Only allows a command if invoked by a user specified in the config.

    Parameters
    ----------
    ctx: commands.Context
        The context in which the command was invoked.

    Returns
    -------
    bool
        True if the invoking user is permitted; False otherwise.
    """
    return ctx.message.author.id in config["user_ids"]


if __name__ == "__main__":
    # Creates loggers.
    format_str: str = "%(asctime)s - [%(levelname)s] %(name)s: %(message)s"
    pattern: Pattern = re.compile(r"Unhandled event", re.IGNORECASE)
    handler: logger.StreamFiltered = logger.StreamFiltered(pattern)

    bot_logger: logger.LoggerProxy = logger.LoggerProxy(
        "", format_str)
    discord_logger: logger.LoggerProxy = logger.LoggerProxy(
        "discord", format_str, handler)
    log = bot_logger.log

    # Loads extensions.
    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
            log.info(f"{extension} loaded successfully.")
        except Exception as e:
            log.error(
                f"{extension} failed to load.\n{type(e).__name__}: {e}")

    bot.run(config["token"])  # Starts the bot.

    # Closes and removes logging handlers.
    bot_logger.close()
    discord_logger.close()
