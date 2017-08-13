from discord.ext import commands
from typing import Dict, List, Match, Pattern
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
        self.pattern = self.getPattern(self.config["words"])

    @staticmethod
    def getPattern(lst: List[str]) -> Pattern:
        """
        Creates a regular expression pattern that will match any string from the
        passed list of strings.

        Parameters
        ----------
        lst: List[str]
            A list of strings from which to create the pattern.

        Returns
        -------
        Pattern
            The compiled regular expression pattern.
        """
        pattern = None

        string: str
        for string in lst:
            if pattern is None:
                # Adds an opening parenthesis before the first string.
                pattern = r"(\b" + string + r"\b"
            else:
                pattern += r"|\b" + re.escape(string) + r"\b"

        pattern += r")"

        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def splitByLength(lst: List[str]) -> Dict[int, List[str]]:
        """
        Splits a list of strings into separate lists which are grouped based on
        the length of the strings.

        These lists are mapped to a dictionary, where the keys are the lengths
        and the values are the lists of strings.

        Parameters
        ----------
        lst: List[str]
            A list of strings to split.

        Returns
        -------
        Dict[int, List[str]]
            A dictionary of lengths and lists of strings which are of those
            lengths.
        """
        # TODO: Sort strings alphabetically.
        out: Dict[int, List[str]] = dict()

        string: str
        for string in lst:
            length: int = len(string)

            # Checks if there are no strings stored for the length of the
            # current string.
            if length not in out.keys():
                # Creates a new list containing the current string.
                out[length] = [string]
            else:
                # Appends to the list which was created above at some earlier
                # point.
                out[length].append(string)

        return out

    async def sendMessage(self, msg: discord.Message, word: str):
        """
        Creates and sends an embed which suggests possible alternatives for the
        word which triggered the Word Police.

        Parameters
        ----------
        msg: discord.Message
            The message which triggered the Word Police.
        word: str
            The word which triggered the Word Police.
        Returns
        -------
        None

        See Also
        -------
        discord.Client.send_message()
        discord.Embed()
        WordPolice.splitByLength()

        """
        embed: discord.Embed = discord.Embed()
        embed.title = "Word Police"
        embed.description = f"Stop right there, {msg.author.mention}!\n" \
                            "Perhaps you meant one of the following words " \
                            "instead?"
        embed.colour = Utils.getRandomColour()
        embed.set_thumbnail(url = self.config["thumbnail"])

        suggestions: Dict[int, List[str]] = self.splitByLength(self.config["words"][word.lower()])

        length: int
        lst: List[str]
        for length, lst in suggestions.items():
            value: str = ""

            for suggestion in lst:
                value += "\n" + suggestion

            embed.add_field(name = f"{length} Letters",
                            value = value)

        await self.bot.send_message(destination = msg.channel, embed = embed)
        self.log.info(f"{msg.author} triggered the word police in "
                      f"{msg.server.name} #{msg.channel.name}")

    async def on_message(self, msg: discord.Message):
        """
        Called when a message is created and sent to a server.

        Determines if the message sent contains a word in the list of words in
        the configuration for WordPolice. If it does, sendMessage() is called.

        Parameters
        ----------
        msg: discord.Message
            The message the creation of which called this event.

        Returns
        -------
        None

        See Also
        --------
        WordPolice.getPattern()
        WordPolice.sendMessage()
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
