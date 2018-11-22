import logging
import re
from typing import Pattern

import discord
from discord.ext import commands
from emoji import unicode_codes

from brotherchris.cogs import utils

log: logging.Logger = logging.getLogger(__name__)


class Commands:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.emoji_pattern = self.get_emoji_pattern()
        self.emoji_custom_pattern = re.compile(r'<:[a-zA-Z0-9_]+:([0-9]+)>$')

    @commands.command()
    @commands.guild_only()
    async def created(
        self,
        ctx: commands.Context,
        channel: discord.abc.GuildChannel = None
    ):
        if channel is None:
            channel = ctx.message.channel

        embed: discord.Embed = discord.Embed()
        embed.colour = discord.Colour(utils.get_random_colour())
        embed.title = 'Channel Info'
        embed.description = f'Channel created at `{channel.created_at}`.'

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def icon(self, ctx: commands.Context, user: discord.User = None):
        await ctx.message.delete()

        embed = discord.Embed()
        embed.colour = discord.Colour(utils.get_random_colour())

        if user is not None:
            embed.title = 'User Avatar'
            embed.description = f'Avatar for {user.mention}.'
            embed.set_image(url=user.avatar_url)

            log_msg = f'{ctx.author} requested {user}\'s avatar.'
        else:
            embed.title = 'Server Icon'
            embed.description = f'Server icon for {ctx.guild.name}.'
            embed.set_image(url=ctx.guild.icon_url)

            log_msg = \
                f'{ctx.author} requested {ctx.guild.name}\'s server icon.'

        await ctx.send(embed=embed)
        log.info(log_msg)

    @commands.command(name='emojiurl')
    async def emoji_url(self, ctx: commands.Context, emoji: str):
        msg = ctx.message
        await msg.delete()

        match = self.emoji_custom_pattern.fullmatch(emoji)

        if match:
            try:
                emoji: discord.Emoji = self.get_custom_emoji(match.group(1))
                await msg.channel.send(emoji.url)
            except discord.InvalidArgument:
                log.error(
                    f'Argument "emoji" ({emoji}) is not a valid custom emoji.')

    @commands.command()
    @commands.guild_only()
    async def id(self, ctx: commands.Context, *, user: discord.User = None):
        if user is None:
            user = ctx.author

        embed = discord.Embed()
        embed.title = 'IDs'
        embed.description = f'IDs for {user.mention}.'
        embed.colour = discord.Colour(utils.get_random_colour())
        embed.add_field(
            name='User:',
            value=user.id,
            inline=False)
        embed.add_field(
            name='Current channel:',
            value=ctx.channel.id,
            inline=False)
        embed.add_field(
            name='Current server:',
            value=ctx.guild.id,
            inline=False)

        await ctx.message.delete()
        await ctx.send(embed=embed)

        log.info(
            f'{ctx.author} retrieved IDs in {ctx.guild.name} '
            f'#{ctx.channel.name}.')

    @commands.command()
    @commands.guild_only()
    async def react(
            self,
            ctx: commands.Context,
            emoji: str,
            limit: int,
            user: discord.User = None
    ):
        await ctx.message.delete()

        if user is None:
            check = None
        else:
            def check(message: discord.Message) -> bool:
                return message.author == user

        async def add_reactions(isCustom: bool = False):
            async for message in utils.get_messages(ctx.channel, limit, check):
                await message.add_reaction(emoji)

            if isCustom:
                emoji_string = emoji
            else:
                emoji_string = emoji.encode('unicode_escape').decode('utf-8')

            log.info(
                f'{ctx.author} reacted with {emoji_string} to {limit} messages '
                f'in {ctx.guild.name} #{ctx.channel.name}.'
            )

        if self.emoji_pattern.fullmatch(emoji):
            await add_reactions()
        else:
            match = self.emoji_custom_pattern.fullmatch(emoji)

            if match:
                try:
                    emoji = self.get_custom_emoji(match.group(1))
                    await add_reactions(True)
                except discord.InvalidArgument:
                    log.error(
                        f'Argument "emoji" ({emoji}) is not a valid custom '
                        f'emoji.'
                    )
            else:
                emoji_string = emoji.encode('unicode_escape').decode('utf-8')
                log.error(
                    f'Argument "emoji" ({emoji_string}) is not a valid '
                    f'Unicode emoji.'
                )

    @staticmethod
    def get_emoji_pattern() -> Pattern:
        emojis = sorted(
            unicode_codes.EMOJI_UNICODE.values(),
            key=len,
            reverse=True
        )

        pattern = (
            u'('
            + u'|'.join(re.escape(e.replace(u' ', u'')) for e in emojis)
            + u')'
        )

        return re.compile(pattern)

    def get_custom_emoji(self, emojiID: str) -> discord.Emoji:
        for emoji in self.bot.emojis:
            if emoji.id == emojiID:
                return emoji

        raise discord.InvalidArgument(
            f'Argument "emojiID" ({emojiID}) does not reference a valid custom '
            f'emoji.'
        )


def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
