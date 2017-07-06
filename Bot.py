from discord.ext import commands
import discord
import json
import re

import Logging

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
async def on_message(msg: discord.Message):
    # if message.author.bot
    if msg.server is not None:
        if msg.author.id == config["id_user"]:
            await bot.process_commands(msg)
        elif msg.server.id == "328315460326129675":
            if re.search(r"(?<!\w)niggers(?!\w)", msg.content, re.IGNORECASE):
                await suggestWord(msg, True)
            elif re.search(r"(?<!\w)nigger(?!\w)", msg.content, re.IGNORECASE):
                await suggestWord(msg)
            elif msg.channel.id == "328315460326129675" and \
                 msg.author.id == "155149108183695360" and \
                 "joined the server! Give them a welcome!" in msg.content:
                await bot.send_message(msg.channel,
                                       f"Welcome {msg.mentions[0].mention}!")
                log.info(f"Welcomed {msg.mentions[0]} in {msg.server.name} "
                         f"#{msg.channel.name}")

async def suggestWord(msg: discord.Message, plural: bool = False):
    if plural:
        s = "s"
        i = 1
    else:
        s = ""
        i = 0

    embed = discord.Embed()
    embed.title = "Word Police"
    embed.description = f"Stop right there, {msg.author.mention}!\n" \
                        "Perhaps you meant one of the following words instead?"
    embed.set_thumbnail(url = "http://clipart-library.com/image_gallery/192486.png")
    embed.add_field(name = f"{6 + i} Letters",
                    value = f"bigger{s}\ndigger{s}\njigger{s}\nrigger{s}")
    embed.add_field(name = f"{7 + i} Letters",
                    value = f"chigger{s}\nsnigger{s}\nswigger{s}\ntrigger{s}")
    embed.add_field(name = f"{8 + i} Letters",
                    value = f"sprigger{s}")

    await bot.send_message(destination = msg.channel, embed = embed)
    log.info(f"{msg.author} triggered the word police in {msg.server.name} "
             f"#{msg.channel.name}")

if __name__ == "__main__":
    # Logging
    strFormat = "%(asctime)s - [%(levelname)s] %(name)s: %(message)s"
    handler = Logging.StreamFiltered(re.compile(r"Unhandled event",
                                                re.IGNORECASE))
    loggerBot = Logging.Logger("bot", strFormat)
    loggerDiscord = Logging.Logger("discord", strFormat, handler)
    log = loggerBot.log

    with open("Configuration.json") as file:
        config = json.load(file)

    for extension in config["extensions"]:
        try:
            bot.load_extension(extension)
        except Exception as e:
            log.log.error(f"{extension} failed to load.\n"
                          f"{type(e).__name__}: {e}")

    bot.run(config["token"], bot = False)

    loggerBot.close()
    loggerDiscord.close()
