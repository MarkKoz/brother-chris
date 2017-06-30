from discord.ext import commands
import discord
import logging
import json

# Logging
lFormat = logging.Formatter("%(asctime)s - [%(levelname)s] %(name)s: %(message)s")

logDiscord = logging.getLogger("discord")
logDiscord.setLevel(logging.INFO)
lHandlerDiscord = logging.StreamHandler()
lHandlerDiscord.setLevel(logging.INFO)
lHandlerDiscord.setFormatter(lFormat)
logDiscord.addHandler(lHandlerDiscord)

logBot = logging.getLogger("bot")
logBot.setLevel(logging.INFO)
lHandlerBot = logging.StreamHandler()
lHandlerBot.setLevel(logging.INFO)
lHandlerBot.setFormatter(lFormat)
logBot.addHandler(lHandlerBot)

config = dict()

prefix = ['?', '!']
description = "Brother Chris"
help_attrs = dict(hidden = True)
bot = commands.Bot(command_prefix = prefix,
                   description = description,
                   self_bot = True,
                   pm_help = None,
                   help_attrs = help_attrs)

@bot.event
async def on_ready():
    logBot.info(f"Brother Chris logged in as {bot.user.name} ({bot.user.id})")

@bot.event
async def on_resumed():
    logBot.info("Brother Chris resumed.")

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id != config["id_user"]:
        return

    await bot.process_commands(message)

if __name__ == "__main__":
    with open("Configuration.json") as file:
        config = json.load(file)

    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            logBot.error(f"{extension} failed to load.\n"
                         f"{type(e).__name__}: {e}")

    bot.run(config["token"], bot = False)
