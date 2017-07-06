from typing import List, Union
import discord
import logging
import re

import cogs.Utils as Utils

class WordPolice:
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("bot.cogs.WordPolice")
        self.log.info("cogs.WordPolice loaded successfully.")
        self.config = Utils.loadConfig("WordPolice")
        self.pattern = self.getPattern()

    def getPattern(self):
        pattern = None

        for word in self.config["words"]:
            if pattern is None:
                pattern = r"(\b" + word + r"\b"
            else:
                pattern += r"|\b" + re.escape(word) + r"\b"

        pattern += r")"

        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def splitByLength(lst: List[str]) -> List[Union[List[str], None]]:
        out = [None] * 16

        for string in lst:
            length = len(string)

            if out[length] is None:
                out[length] = [string]
            else:
                out[length].append(string)

        return out

    async def sendMessage(self, msg: discord.Message, word: str):
        embed = discord.Embed()
        embed.title = "Word Police"
        embed.description = f"Stop right there, {msg.author.mention}!\n" \
                            "Perhaps you meant one of the following words instead?"
        embed.colour = Utils.getRandomColour()
        embed.set_thumbnail(url = self.config["thumbnail"])

        for i, length in enumerate(self.splitByLength(self.config["words"][word])):
            if length is not None:
                value = None

                for suggestion in length:
                    if value is None:
                        value = suggestion
                    else:
                        value += "\n" + suggestion

                embed.add_field(name = f"{i} Letters",
                                value = value)

        await self.bot.send_message(destination = msg.channel, embed = embed)
        self.log.info(f"{msg.author} triggered the word police in "
                      f"{msg.server.name} #{msg.channel.name}")

    async def on_message(self, msg: discord.Message):
        if msg.server is None:
            return

        if msg.server.id in self.config["idServers"]:
            match = re.search(self.pattern, msg.content)

            if match:
                await self.sendMessage(msg, match.group(1))


def setup(bot):
    bot.add_cog(WordPolice(bot))
