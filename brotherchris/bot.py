import logging
import traceback

import discord
from discord.ext import commands

from brotherchris.cogs import utils

log: logging.Logger = logging.getLogger(__name__)
config: dict = utils.load_config('Bot')


class BrotherChris(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config['prefixes'],
            description=config['name'],
            pm_help=None,
            help_attrs=dict(hidden=True)
        )

        self.add_check(self.global_user_check)

    async def on_ready(self):
        """
        Called when the :class:`client<discord.Client>` is done preparing the
        data received from Discord. Usually after login is successful and the
        Client.servers and co. are filled up.

        Note
        -------
        This function is not guaranteed to be the first event called. Likewise,
        this function is not guaranteed to only be called once. This library
        implements reconnection logic and thus will end up calling this event
        whenever a RESUME request fails.

        Returns
        -------
        None
        """
        log.info(
            f'{self.description} logged in as {self.user} ({self.user.id})')

    async def on_resumed(self):
        """
        Called when the :class:`client<discord.Client>` has resumed a session.

        Returns
        -------
        None
        """
        log.info(f'{self.description} resumed.')

    async def on_message(self, msg: discord.Message):
        """
        Called when a :class:`message<discord.Message>` is created and sent to a
        server.

        Parameters
        ----------
        msg: discord.Message
            The message the creation of which called this event.

        Returns
        -------
        None
        """
        if not msg.author.bot:
            await self.process_commands(msg)

    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError
    ):
        """
        An error handler that is called when an error is raised inside a
        command.

        Parameters
        ----------
        ctx: commands.Context
            The context in which the command was invoked.
        error: commands.CommandError
            The error that was raised.

        Returns
        -------
        None
        """
        # Skips errors that were already handled locally.
        if getattr(ctx, 'handled', False):
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in direct messages.')
        elif isinstance(error, commands.TooManyArguments):
            await ctx.send('Too many arguments.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Missing required argument `{error.param.name}`.')
        elif isinstance(error, commands.NotOwner) or \
                isinstance(error, commands.MissingPermissions):
            await ctx.send(
                'You do not have the required permissions to invoke this '
                'command.')
        elif isinstance(error, commands.CommandOnCooldown) or \
                isinstance(error, commands.CheckFailure):
            await ctx.send(error)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(
                f'This command is currently disabled and cannot be used.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f'Bad argument: {error}')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                'Oops! The bot does not have the required permissions to '
                'execute this command.')
            log.error(
                f'{ctx.command.qualified_name} cannot be executed because the '
                f'bot is missing the following permissions: '
                f'{", ".join(error.list)}')
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send('Something went wrong internally!')
            log.error(
                f'{ctx.command.qualified_name} failed to execute. '
                f'{error.original.__class__.__name__}: {error.original}\n'
                f'{"".join(traceback.format_tb(error.original.__traceback__))}')

    @staticmethod
    async def global_user_check(ctx: commands.Context) -> bool:
        """
        Only allows a command if invoked by a user specified in the config.

        Parameters
        ----------
        ctx: commands.Context
            The context in which the command was invoked.

        Returns
        -------
        bool
            True if the invoking user is permitted.

        Raises
        ------
        commands.CheckFailure
            If the invoking user is not permitted.
        """
        if ctx.message.author.id not in config['user_ids']:
            raise commands.CheckFailure(
                'Sorry, you are not whitelisted to use commands.')

        return True
