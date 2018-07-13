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
    # Ignores direct/private messages.
    if msg.guild is None:
        return

    # Only processes commands if called by users as specified in the config.
    if msg.author.id in config["user_ids"]:
        await bot.process_commands(msg)

if __name__ == "__main__":
    # Creates loggers.
    strFormat: str = "%(asctime)s - [%(levelname)s] %(name)s: %(message)s"
    pattern: Pattern = re.compile(r"Unhandled event", re.IGNORECASE)
    handler: logger.StreamFiltered = logger.StreamFiltered(pattern)

    loggerBot: logger.LoggerProxy = logger.LoggerProxy("bot", strFormat)
    loggerDiscord: logger.LoggerProxy = logger.LoggerProxy("discord", strFormat, handler)
    log = loggerBot.log

    # Loads extensions.
    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.error(f"{extension} failed to load.\n"
                      f"{type(e).__name__}: {e}")

    bot.run(config["token"]) # Starts the bot.

    # Closes and removes logging handlers.
    loggerBot.close()
    loggerDiscord.close()
