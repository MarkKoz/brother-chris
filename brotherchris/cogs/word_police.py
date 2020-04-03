import logging
import re
from itertools import groupby
from typing import Dict, Iterator, List, Pattern, Tuple

import discord
from discord.ext import commands

from brotherchris.cogs import utils

log: logging.Logger = logging.getLogger(__name__)


class WordPolice:
    """
    Sends a message with word suggestions when a blacklisted word is found in a
    sent message.
    """

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.config: Dict = utils.load_config('WordPolice')
        self.pattern = self.get_pattern(self.config['words'])

    @staticmethod
    def get_pattern(lst: List[str]) -> Pattern:
        """
        Creates a regular expression :class:`Pattern` that will match any
        :class:`string<str>` from :any:`lst`.

        Parameters
        ----------
        lst: List[str]
            A list of strings from which to create the pattern.

        Returns
        -------
        Pattern
            The compiled regular expression pattern.
        """
        pattern: str = None
        for string in lst:
            if pattern is None:
                # Adds an opening parenthesis before the first string.
                pattern = fr'(\b{string}\b'
            else:
                pattern += fr'|\b{re.escape(string)}\b'

        pattern += r')'
        return re.compile(pattern, re.IGNORECASE)

    @staticmethod
    def group_by_length(lst: List[str]) -> Iterator[Tuple[int, Iterator[str]]]:
        """
        Group strings in `lst` by their lengths and sort each group
        alphabetically.

        Parameters
        ----------
        lst: List[str]
            A list of strings to group.

        Returns
        -------
        Iterator[Tuple[int, Iterator[str]]]
            Tuples of lengths and lists of strings which are of those
            lengths.
        """
        lst.sort(key=lambda s: (len(s), s))
        return groupby(lst, key=len)

    async def send_message(self, msg: discord.Message, word: str):
        """
        Create and send an :class:`embed<discord.Embed>` which suggests
        possible alternatives for the word which triggered the Word Police.

        Parameters
        ----------
        msg: discord.Message
            The message which triggered the Word Police.
        word: str
            The word which triggered the Word Police.
        """
        embed: discord.Embed = discord.Embed()
        embed.title = 'Word Police'
        embed.description = \
            f'Stop right there, {msg.author.mention}!\n' \
            f'Perhaps you meant one of the following words instead?'
        embed.colour = utils.get_random_colour()
        embed.set_thumbnail(url=self.config['thumbnail'])

        suggestions = self.group_by_length(self.config['words'][word.lower()])

        for length, lst in suggestions:
            embed.add_field(name=f'{length} Letters', value='\n'.join(lst))

        await msg.channel.send(embed=embed)
        log.info(
            f'{msg.author} triggered the word police in {msg.guild.name} '
            f'#{msg.channel.name}'
        )

    async def on_message(self, msg: discord.Message):
        """
        Called when a :class:message`<discord.Message>` is created and sent to a
        server.

        Determines if the message sent contains words in the list of words in
        the configuration for WordPolice. If it does, :func:`send_message` is
        called for every unique match.

        Parameters
        ----------
        msg: discord.Message
            The message the creation of which called this event.
        """
        # Ignores direct messages.
        if msg.author.bot or msg.guild is None:
            return

        # Only processes messages which come from the servers specified in the
        # configuration.
        if msg.guild.id in self.config['server_ids']:
            matches = re.findall(self.pattern, msg.content)

            # Iterates through every unique match in order of appearance.
            for match in dict.fromkeys(matches):
                await self.send_message(msg, match)


def setup(bot: commands.Bot):
    bot.add_cog(WordPolice(bot))
