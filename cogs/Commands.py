from discord.ext import commands
from emoji import unicode_codes
from typing import AsyncGenerator, Callable, List, Match, Pattern
from wordcloud import WordCloud
import discord
import logging
import pathlib
import re
import sys

import cogs.Utils as Utils

class Commands:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.log: logging.Logger = logging.getLogger("bot.cogs.Commands")
        self.log.info("cogs.Commands loaded successfully.")
        self.emojiPattern: Pattern = self.getEmojiPattern()
        self.emojiCustomPattern: Pattern = re.compile(r"<:[a-zA-Z0-9_]+:([0-9]+)>$")

    @commands.command(pass_context = True)
    async def icon(self, ctx, user: discord.User = None):
        msg: discord.Message = ctx.message

        # Deletes the command message.
        await self.bot.delete_message(msg)

        embed: discord.Embed = discord.Embed()
        embed.colour = discord.Colour(Utils.getRandomColour())

        if user is not None:
            embed.title = "User Avatar"
            embed.description = f"Avatar for {user.mention}."
            embed.set_image(url = user.avatar_url)

            logMsg: str = f"{msg.author} requested {user}'s avatar."
        else:
            embed.title = "Server Icon"
            embed.description = f"Server icon for {msg.server.name}."
            embed.set_image(url = msg.server.icon_url)

            logMsg: str = f"{msg.author} requested {msg.server.name}'s " \
                          f"server icon."

        await self.bot.send_message(destination = msg.channel, embed = embed)
        self.log.info(logMsg)

    @commands.command(pass_context = True)
    async def id(self, ctx, *, user: discord.User = None):
        msg: discord.Message = ctx.message

        if user is None:
            user = msg.author

        embed: discord.Embed = discord.Embed()
        embed.title = "IDs"
        embed.description = f"IDs for {user.mention}."
        embed.colour = discord.Colour(Utils.getRandomColour())
        embed.add_field(name = "User:",
                        value = user.id,
                        inline = False)
        embed.add_field(name = "Current channel:",
                        value = msg.channel.id,
                        inline = False)
        embed.add_field(name = "Current server:",
                        value = msg.server.id,
                        inline = False)

        await self.bot.delete_message(msg)
        await self.bot.send_message(destination = msg.channel, embed = embed)

        self.log.info(f"{msg.author} retrieved IDs in {msg.server.name} "
                      f"#{msg.channel.name}.")

    @commands.command(pass_context = True)
    async def react(self, ctx, emoji: str, limit: int, user: discord.User = None):
        msg: discord.Message = ctx.message
        await self.bot.delete_message(msg)

        if user is None:
            check = None
        else:
            def check(message: discord.Message) -> bool:
                return message.author == user

        async def addReactions(isCustom: bool = False):
            async for message in self.getMessages(msg.channel, limit, check):
                await self.bot.add_reaction(message, emoji)

            if isCustom:
                # TODO: Add type annotations for emojiString.
                emojiString = emoji
            else:
                emojiString = emoji.encode("unicode_escape").decode("utf-8")

            self.log.info(f"{msg.author} reacted with {emojiString} to "
                          f"{limit} messages in {msg.server.name} "
                          f"#{msg.channel.name}.")

        if self.emojiPattern.fullmatch(emoji):
            await addReactions()
        else:
            match: Match = self.emojiCustomPattern.fullmatch(emoji)

            if match:
                try:
                    emoji: discord.Emoji = self.getEmojiCustom(match.group(1))
                    await addReactions(True)
                except discord.InvalidArgument:
                    self.log.error(f"Argument 'emoji' ({emoji}) is not a valid "
                                   "custom emoji.")
            else:
                emojiString = emoji.encode("unicode_escape").decode("utf-8")
                self.log.error(f"Argument 'emoji' ({emojiString}) is not a "
                               "valid Unicode emoji.")

    @commands.command(pass_context = True)
    async def wc(self,
                 ctx,
                 user: discord.User = None,
                 channel: discord.Channel = None,
                 limit: int = 1000,
                 colour: str = None):
        msg: discord.Message = ctx.message

        if user is None:
            user = msg.author

        if channel is None:
            channel = msg.channel

        # Deletes the command message.
        await self.bot.delete_message(msg)

        # Generates and posts a word cloud.
        imageFile: pathlib.Path = await self.getWordCloudImage(channel, user, limit, colour)
        await self.bot.send_file(msg.channel, imageFile)
        pathlib.Path.unlink(imageFile)

        # Retrieves the word cloud attachment's URL.
        # def check(message: discord.Message) -> bool:
        #     if message.attachments:
        #         return dict(message.attachments[0])["filename"] == os.path.basename(imageFile)
        #
        #     return False
        #
        # imageMessage = await self.bot.wait_for_message(author = msg.author,
        #                                                check = check)
        # imageURL: str = dict(imageMessage.attachments[0])["url"]
        # await self.bot.delete_message(imageMessage)

        # Embed properties.
        embed: discord.Embed = discord.Embed()
        embed.title = "Word Cloud"
        embed.description = f"Word cloud for {user.mention} in " \
                            f"{channel.mention}."
        embed.colour = discord.Colour(Utils.getRandomColour())
        # embed.set_image(url = imageURL)

        await self.bot.send_message(destination = msg.channel, embed = embed)

        self.log.info(f"{msg.author} generated a word cloud for {user} in "
                      f"{channel.server.name} #{channel.name}.")

    @staticmethod
    async def getContents(messages: AsyncGenerator[discord.Message, None]) -> str:
        contents: str = ""

        async for message in messages:
            contents += f"{message.content}\n"

        return contents

    @staticmethod
    def getEmojiPattern() -> Pattern:
        emojis: List[str] = sorted(unicode_codes.EMOJI_UNICODE.values(),
                                   key = len,
                                   reverse = True)
        pattern = u"(" + u"|".join(re.escape(e.replace(u" ", u"")) for e in emojis) + u")"

        return re.compile(pattern)

    async def getMessages(self,
                          channel: discord.Channel,
                          limit: int,
                          check: Callable[[discord.Message], bool] = None
                          ) -> AsyncGenerator[discord.Message, None]:
        counter: int = 0
        limitLogs: int = 1000

        if limit > limitLogs:
            limitLogs = limit

        async for message in self.bot.logs_from(channel, limitLogs):
            if (check is None or check(message)) and counter != limit:
                counter += 1
                yield message

    def getEmojiCustom(self, emojiID: str) -> discord.Emoji:
        for emoji in self.bot.get_all_emojis():
            if emoji.id == emojiID:
                return emoji

        raise discord.InvalidArgument(f"Argument 'emojiID' ({emojiID}) does not"
                                      " reference a valid custom emoji.")

    async def getWordCloudImage(self,
                                channel: discord.Channel,
                                user: discord.User,
                                limit: int,
                                colour: str
                                ) -> pathlib.Path:
        def check(message: discord.Message) -> bool:
            return message.author == user

        # Generates the word cloud.
        text: str = await self.getContents(self.getMessages(channel, limit, check))
        wordcloud: WordCloud = WordCloud(width = 1280,
                                         height = 720,
                                         background_color = colour,
                                         mode = "RGBA"
                                         ).generate(text)

        # TODO: Put path-related code into a separate function.
        # Creates the path to the file to which the image will be saved.
        path: pathlib.Path = pathlib.Path(sys.modules['__main__'].__file__).with_name(".temp_wc")

        if not path.exists():
            self.log.info(f"{path.name} does not exist; it will be created.")

        path.mkdir(parents = True, exist_ok = True)
        path = path.joinpath(f"wc_{user.id}.png")

        wordcloud.to_file(str(path))

        return path

def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))
