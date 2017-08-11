from discord.ext import commands
from typing import Dict, List, Match, Pattern, Union
import discord
import logging
import re

import cogs.Utils as Utils

class WordPolice:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.log: logging.Logger = logging.getLogger("bot.cogs.WordPolice")
        self.log.info("cogs.WordPolice loaded successfully.")
        self.config: Dict = Utils.loadConfig("WordPolice")
        self.pattern = self.getPattern()

    def getPattern(self) -> Pattern:
        """
        Creates a regular expression pattern that will match any word from the
        list of words in the configuration for WordPolice.

        Returns
        -------
        Pattern
            The compiled regular expression pattern.
        """
        pattern = None

        word: str
        for word in self.config["words"]:
            if pattern is None:
                pattern = r"(\b" + word + r"\b"
            else:
                pattern += r"|\b" + re.escape(word) + r"\b"

        pattern += r")"

        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def splitByLength(lst: List[str]) -> List[Union[List[str], None]]:
        """
        Splits a list of strings into separate lists which are grouped based on
        the length of the strings.

        These lists are then stored into a list which can be accessed by an
        index which is equivalent to the length of the words of the list at that
        index.

        If no strings of a length equivalent to a given index exist, then the
        object at that index will be None.

        Maximum supported string length is 16 characters.

        Parameters
        ----------
        lst: List[str]
            A list of strings to split.

        Returns
        -------
        List[Union[List[str], None]]
            A list of the lists of split words.
        """
        # TODO: Remove hard-coded character limit.
        # TODO: Output a dictionary instead of a list.
        out: List[Union[List[str], None]] = [None] * 16

        for string in lst:
            length: int = len(string)

            if out[length] is None:
                out[length] = [string]
            else:
                out[length].append(string)

        return out

    async def sendMessage(self, msg: discord.Message, word: str):
        embed: discord.Embed = discord.Embed()
        embed.title = "Word Police"
        embed.description = f"Stop right there, {msg.author.mention}!\n" \
                            "Perhaps you meant one of the following words " \
                            "instead?"
        embed.colour = Utils.getRandomColour()
        embed.set_thumbnail(url = self.config["thumbnail"])

        i: int
        length: int
        for i, length in enumerate(self.splitByLength(self.config["words"][word.lower()])):
            if length is not None:
                value: str = None

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
        """
        An event handler for sent messages.

        Determines if the message sent contains a word in the list of words in
        the configuration for WordPolice.

        Parameters
        ----------
        msg: discord.Message
            The sent message which triggered this event handler.

        Returns
        -------
        None

        See Also
        --------
        getPattern()
        """
        # Ignores direct messages.
        if msg.server is None:
            return

        # Searches the message with the regular expression.
        if msg.server.id in self.config["idServers"]:
            match: Match = re.search(self.pattern, msg.content)

            if match:
                await self.sendMessage(msg, match.group(1))


def setup(bot: commands.Bot):
    bot.add_cog(WordPolice(bot))
