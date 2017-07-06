from discord.ext import commands
import discord
import json
import re

import Logging

# Loads the configuration file.
with open("Configuration.json") as file:
    config = json.load(file)["Bot"]

name = config["name"]
bot = commands.Bot(command_prefix = config["prefixes"],
                   description = name,
                   self_bot = True,
                   pm_help = None,
                   help_attrs = dict(hidden = True))

@bot.event
async def on_ready():
    log.info(f"{name} logged in as {bot.user.name} ({bot.user.id})")

@bot.event
async def on_resumed():
    log.info(f"{name} resumed.")

@bot.event
async def on_message(msg: discord.Message):
    if msg.server is None:
        return

    if msg.author.id in config["idUsers"]:
        await bot.process_commands(msg)

if __name__ == "__main__":
    # Creates loggers.
    strFormat = "%(asctime)s - [%(levelname)s] %(name)s: %(message)s"
    handler = Logging.StreamFiltered(re.compile(r"Unhandled event",
                                                re.IGNORECASE))
    loggerBot = Logging.Logger("bot", strFormat)
    loggerDiscord = Logging.Logger("discord", strFormat, handler)
    log = loggerBot.log

    # Loads extensions.
    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.log.error(f"{extension} failed to load.\n"
                          f"{type(e).__name__}: {e}")

    bot.run(config["token"], bot = False)

    # Closes and removes logging handlers.
    loggerBot.close()
    loggerDiscord.close()
