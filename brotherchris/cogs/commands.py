import logging
import re
from typing import List, Match, Pattern

import discord
from discord.ext import commands
from emoji import unicode_codes

from brotherchris.cogs import utils

log: logging.Logger = logging.getLogger(__name__)


class Commands:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.emoji_pattern: Pattern = self.get_emoji_pattern()
        self.emoji_custom_pattern: Pattern = re.compile(
            r"<:[a-zA-Z0-9_]+:([0-9]+)>$")

    @commands.command()
    @commands.guild_only()
    async def created(
            self,
            ctx: commands.Context,
            channel: discord.abc.GuildChannel = None):
        msg: discord.Message = ctx.message

        if channel is None:
            channel = msg.channel

        embed: discord.Embed = discord.Embed()
        embed.colour = discord.Colour(utils.get_random_colour())
        embed.title = "Channel Info"
        embed.description = f"Channel created at `{channel.created_at}`."

        await msg.channel.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def icon(self, ctx: commands.Context, user: discord.User = None):
        msg: discord.Message = ctx.message

        # Deletes the command message.
        await msg.delete()

        embed: discord.Embed = discord.Embed()
        embed.colour = discord.Colour(utils.get_random_colour())

        if user is not None:
            embed.title = "User Avatar"
            embed.description = f"Avatar for {user.mention}."
            embed.set_image(url=user.avatar_url)

            log_msg: str = f"{msg.author} requested {user}'s avatar."
        else:
            embed.title = "Server Icon"
            embed.description = f"Server icon for {msg.guild.name}."
            embed.set_image(url=msg.guild.icon_url)

            log_msg: str = \
                f"{msg.author} requested {msg.guild.name}'s server icon."

        await msg.channel.send(embed=embed)
        log.info(log_msg)

    @commands.command(name="emojiurl")
    async def emoji_url(self, ctx: commands.Context, emoji: str):
        msg: discord.Message = ctx.message
        await msg.delete()

        match: Match = self.emoji_custom_pattern.fullmatch(emoji)

        if match:
            try:
                emoji: discord.Emoji = self.get_custom_emoji(match.group(1))
                await msg.channel.send(emoji.url)
            except discord.InvalidArgument:
                log.error(
                    f"Argument 'emoji' ({emoji}) is not a valid custom emoji.")

    @commands.command()
    @commands.guild_only()
    async def id(self, ctx: commands.Context, *, user: discord.User = None):
        msg: discord.Message = ctx.message

        if user is None:
            user = msg.author

        embed: discord.Embed = discord.Embed()
        embed.title = "IDs"
        embed.description = f"IDs for {user.mention}."
        embed.colour = discord.Colour(utils.get_random_colour())
        embed.add_field(
            name="User:",
            value=user.id,
            inline=False)
        embed.add_field(
            name="Current channel:",
            value=msg.channel.id,
            inline=False)
        embed.add_field(
            name="Current server:",
            value=msg.guild.id,
            inline=False)

        await msg.delete()
        await msg.channel.send(embed=embed)

        log.info(
            f"{msg.author} retrieved IDs in {msg.guild.name} "
            f"#{msg.channel.name}.")

    @commands.command()
    @commands.guild_only()
    async def react(
            self,
            ctx: commands.Context,
            emoji: str,
            limit: int,
            user: discord.User = None):
        msg: discord.Message = ctx.message
        await msg.delete()

        if user is None:
            check = None
        else:
            def check(message: discord.Message) -> bool:
                return message.author == user

        async def add_reactions(isCustom: bool = False):
            async for message in utils.get_messages(msg.channel, limit, check):
                await message.add_reaction(emoji)

            if isCustom:
                # TODO: Add type annotations for emoji_string.
                emoji_string = emoji
            else:
                emoji_string = emoji.encode("unicode_escape").decode("utf-8")

            log.info(
                f"{msg.author} reacted with {emoji_string} to {limit} messages "
                f"in {msg.guild.name} #{msg.channel.name}.")

        if self.emoji_pattern.fullmatch(emoji):
            await add_reactions()
        else:
            match: Match = self.emoji_custom_pattern.fullmatch(emoji)

            if match:
                try:
                    emoji: discord.Emoji = self.get_custom_emoji(match.group(1))
                    await add_reactions(True)
                except discord.InvalidArgument:
                    log.error(
                        f"Argument 'emoji' ({emoji}) is not a valid custom "
                        f"emoji.")
            else:
                emoji_string = emoji.encode("unicode_escape").decode("utf-8")
                log.error(
                    f"Argument 'emoji' ({emoji_string}) is not a valid "
                    f"Unicode emoji.")

    @staticmethod
    def get_emoji_pattern() -> Pattern:
        emojis: List[str] = sorted(
            unicode_codes.EMOJI_UNICODE.values(),
            key=len,
            reverse=True)

        pattern = u"(" + \
            u"|".join(re.escape(e.replace(u" ", u"")) for e in emojis) + \
            u")"

        return re.compile(pattern)

    def get_custom_emoji(self, emojiID: str) -> discord.Emoji:
        for emoji in self.bot.emojis:
            if emoji.id == emojiID:
                return emoji

        raise discord.InvalidArgument(
            f"Argument 'emojiID' ({emojiID}) does not reference a valid custom "
            f"emoji.")


def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
