import logging
from typing import Dict

import discord
from discord.ext import commands

from brotherchris.cogs import utils

log: logging.Logger = logging.getLogger(__name__)


class Welcome(commands.Cog):
    """
    Welcomes users welcomed by the Dyno bot.
    """

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.config: Dict = utils.load_config('Welcome')

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """
        Called when a :class:`message<discord.Message>` is created and sent to a
        server.

        Determines if the message sent is a welcome message from the Dyno bot.
        If it is, a welcome message is sent which mentions the same user the
        Dyno bot welcomed.

        Parameters
        ----------
        msg: discord.Message
            The message the creation of which called this event.

        Returns
        -------
        None

        See Also
        -------
        discord.Client.send_message()
        """
        # Ignores direct messages.
        if msg.guild is None:
            return

        # Only processes messages which come from the servers specified in the
        # configuration.
        # Checks if the author is the Dyno bot and if the message contains
        # the welcome string specified in the configuration.
        if (
            msg.channel.id in self.config['channels']
            and msg.author.id == self.config['dyno_id']
            and self.config['dyno_msg'] in msg.content
        ):
            await msg.channel.send(f'Welcome {msg.mentions[0].mention}!')
            log.info(
                f'Welcomed {msg.mentions[0]} in {msg.guild.name} '
                f'#{msg.channel.name}'
            )


def setup(bot: commands.Bot):
    bot.add_cog(Welcome(bot))
