from discord.ext import commands
import discord
import logging
import json

# logging.basicConfig(level = logging.WARNING)
log = logging.getLogger("bot")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

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
    log.info(f"Brother Chris logged in as {bot.user.name} ({bot.user.id})")

@bot.event
async def on_resumed():
    log.info("Brother Chris resumed.")

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
            log.error(f"{extension} failed to load.\n"
                      f"{type(e).__name__}: {e}")

    bot.run(config["token"], bot = False)
