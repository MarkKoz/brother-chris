from typing import Pattern
import re

from discord.ext import commands
import discord

from cogs import utils
import logger

# Loads the configuration file.
config: dict = utils.load_config("Bot")
name: str = config["name"]

bot: commands.Bot = commands.Bot(command_prefix = config["prefixes"],
                                 description = name,
                                 pm_help = None,
                                 help_attrs = dict(hidden = True))

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

    bot_logger: logger.LoggerProxy = logger.LoggerProxy("bot", format_str)
    discord_logger: logger.LoggerProxy = logger.LoggerProxy("discord", format_str, handler)
    log = bot_logger.log

    # Loads extensions.
    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error(f"{extension} failed to load.\n"
                      f"{type(e).__name__}: {e}")

    bot.run(config["token"]) # Starts the bot.

    # Closes and removes logging handlers.
    bot_logger.close()
    discord_logger.close()
