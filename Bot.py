from discord.ext import commands
import discord
import json

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
    print("Brother Chris logged in.\n"
          f"\tUsername: {bot.user.name}\n"
          f"\tID: {bot.user.id}\n")

@bot.event
async def on_resumed():
    print("\nBrother Chris resumed.\n")

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
            print(f"Error loading extension {extension}\n"
                  f"{type(e).__name__}: {e}")

    bot.run(config["token"], bot = False)
