import discord
import json
import logging

import cogs.Utils as Utils

class Welcome:
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("bot.cogs.Welcome")
        self.log.info("cogs.Welcome loaded successfully.")
        self.config = Utils.loadConfig("Welcome")

    async def on_message(self, msg: discord.Message):
        if msg.server is None:
            return

        if msg.channel.id in self.config["channels"] and \
           msg.author.id == self.config["idDyno"] and \
           self.config["msgDyno"] in msg.content:
            await self.bot.send_message(msg.channel,
                                        f"Welcome {msg.mentions[0].mention}!")
            self.log.info(f"Welcomed {msg.mentions[0]} in {msg.server.name} "
                          f"#{msg.channel.name}")

def setup(bot):
    bot.add_cog(Welcome(bot))