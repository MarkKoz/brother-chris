from typing import AsyncGenerator, Callable, List, Match, Pattern
import logging
import pathlib
import re
import sys

from discord.ext import commands
from emoji import unicode_codes
from wordcloud import WordCloud
import discord

from cogs import utils

class Commands:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.log: logging.Logger = logging.getLogger("bot.cogs.Commands")
        self.log.info("cogs.Commands loaded successfully.")
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
        self.log.info(log_msg)

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
                self.log.error(
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

        self.log.info(
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
            async for message in self.get_messages(msg.channel, limit, check):
                await message.add_reaction(emoji)

            if isCustom:
                # TODO: Add type annotations for emoji_string.
                emoji_string = emoji
            else:
                emoji_string = emoji.encode("unicode_escape").decode("utf-8")

            self.log.info(
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
                    self.log.error(
                        f"Argument 'emoji' ({emoji}) is not a valid custom "
                        f"emoji.")
            else:
                emoji_string = emoji.encode("unicode_escape").decode("utf-8")
                self.log.error(
                    f"Argument 'emoji' ({emoji_string}) is not a valid "
                    f"Unicode emoji.")

    @commands.command(name="wc")
    @commands.guild_only()
    async def word_cloud(
            self,
            ctx: commands.Context,
            user: discord.User = None,
            channel: discord.TextChannel = None,
            limit: int = 1000,
            colour: str = None):
        msg: discord.Message = ctx.message

        if user is None:
            user = msg.author

        if channel is None:
            channel = msg.channel

        # Deletes the command message.
        await msg.delete()

        # Generates and posts a word cloud.
        image_path: pathlib.Path = await self.get_word_cloud_image(
            channel, user, limit, colour)

        await msg.channel.send(file=discord.File(image_path))
        pathlib.Path.unlink(image_path)

        # Embed properties.
        embed: discord.Embed = discord.Embed()
        embed.title = "Word Cloud"
        embed.description = \
            f"Word cloud for {user.mention} in {channel.mention}."
        embed.colour = discord.Colour(utils.get_random_colour())
        # embed.set_image(url = imageURL)

        await msg.channel.send(embed=embed)

        self.log.info(f"{msg.author} generated a word cloud for {user} in "
                      f"{channel.guild.name} #{channel.name}.")

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

    @staticmethod
    async def get_messages(
            channel: discord.TextChannel,
            limit: int,
            check: Callable[[discord.Message], bool] = None
            ) -> AsyncGenerator[discord.Message, None]:
        counter: int = 0
        history_limit: int = 1000

        if limit > history_limit:
            history_limit = limit

        async for message in channel.history(limit = history_limit):
            if (check is None or check(message)) and counter != limit:
                counter += 1
                yield message

    def get_custom_emoji(self, emojiID: str) -> discord.Emoji:
        for emoji in self.bot.emojis:
            if emoji.id == emojiID:
                return emoji

        raise discord.InvalidArgument(
            f"Argument 'emojiID' ({emojiID}) does not reference a valid custom "
            f"emoji.")

    async def get_word_cloud_image(
            self,
            channel: discord.TextChannel,
            user: discord.User,
            limit: int,
            colour: str
            ) -> pathlib.Path:
        def check(message: discord.Message) -> bool:
            return message.author == user

        # Generates the word cloud.
        text: str = "\n".join(
            m.content async for m in self.get_messages(channel, limit, check))

        word_cloud: WordCloud = WordCloud(
            width=1280,
            height=720,
            background_color=colour,
            mode="RGBA"
            ).generate(text)

        # TODO: Put path-related code into a separate function.
        # Creates the path to the file to which the image will be saved.
        path: pathlib.Path = pathlib.Path(sys.modules['__main__'].__file__)\
            .with_name(".temp_wc")

        if not path.exists():
            self.log.info(f"{path.name} does not exist; it will be created.")

        path.mkdir(parents=True, exist_ok=True)
        path = path.joinpath(f"wc_{user.id}.png")

        word_cloud.to_file(str(path))

        return path

def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
