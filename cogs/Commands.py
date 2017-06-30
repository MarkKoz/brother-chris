from discord.ext import commands
from randomcolor import RandomColor
from typing import Callable, Generator
from wordcloud import WordCloud
import discord
import emoji as Emoji
import logging
import pathlib
import re
import sys

class Commands:
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("bot.cogs.Commands")
        self.log.info("cogs.Commands loaded successfully.")

    @commands.command(pass_context = True)
    async def id(self, ctx, *, user: discord.User = None):
        msg = ctx.message

        if user is None:
            user = msg.author

        embed = discord.Embed()
        embed.title = "IDs"
        embed.description = f"IDs for {user.mention}."
        embed.colour = discord.Colour(self.getRandomColour())
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
    async def react(self, ctx, emoji: str, limit: int = 100):
        msg = ctx.message
        await self.bot.delete_message(msg)

        async def addReactions():
            async for message in self.bot.logs_from(msg.channel, limit):
                await self.bot.add_reaction(message, emoji)

            self.log.info(f"{msg.author} reacted with {emoji} to "
                          f"{limit} messages in {msg.server.name} "
                          f"#{msg.channel.name}.")

        if Emoji.get_emoji_regexp().fullmatch(emoji):
            await addReactions()
        else:
            pattern = re.compile(r"<:[a-zA-Z0-9_]+:([0-9]+)>$")
            match = pattern.fullmatch(emoji)

            if match:
                try:
                    emoji = self.getEmoji(match.group(1))
                    await addReactions()
                except discord.InvalidArgument:
                    self.log.error(f"Argument 'emoji' ({emoji}) is not a valid "
                                   "custom emoji.")
            else:
                self.log.error(f"Argument 'emoji' ({emoji}) is not a valid "
                               "Unicode emoji.")

    @commands.command(pass_context = True)
    async def wc(self,
                 ctx,
                 user: discord.User = None,
                 channel: discord.Channel = None,
                 limit: int = 1000,
                 colour: str = None):
        msg = ctx.message

        if user is None:
            user = msg.author

        if channel is None:
            channel = msg.channel

        # Deletes the command message.
        await self.bot.delete_message(msg)

        # Generates and posts a word cloud.
        imageFile = await self.getWordCloudImage(channel, user, limit, colour)
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
        # imageURL = dict(imageMessage.attachments[0])["url"]
        # await self.bot.delete_message(imageMessage)

        # Embed properties.
        out = discord.Embed()
        out.title = "Word Cloud"
        out.description = f"Word cloud for {user.mention} in {channel.mention}."
        out.colour = discord.Colour(self.getRandomColour())
        # out.set_image(url = imageURL)

        await self.bot.send_message(destination = msg.channel, embed = out)

        self.log.info(f"{msg.author} generated a word cloud for {user} in "
                      f"{channel.server.name} #{channel.name}.")

    @staticmethod
    def getRandomColour() -> int:
        return int(RandomColor().generate()[0].lstrip('#'), 16)

    @staticmethod
    async def getContents(messages) -> str:
        contents = ""

        async for message in messages:
            contents += f"{message.content}\n"

        return contents

    async def getMessages(self,
                          channel: discord.Channel,
                          limit: int,
                          check: Callable[[discord.Message], bool] = None
                          ) -> Generator[discord.Message, None, None]:
        async for message in self.bot.logs_from(channel, limit):
            if check is None or check(message):
                yield message

    def getEmoji(self, emojiID: str) -> discord.Emoji:
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
        text = await self.getContents(self.getMessages(channel, limit, check))
        wordcloud = WordCloud(width = 1280,
                              height = 720,
                              background_color = colour,
                              mode = "RGBA"
                              ).generate(text)

        # Creates the path to the file to which the image will be saved.
        path = pathlib.Path(sys.modules['__main__'].__file__).with_name(".temp_wc")

        if not path.exists():
            self.log.info(f"{path.name} does not exist; it will be created.")

        path.mkdir(parents = True, exist_ok = True)
        path = path.joinpath(f"wc_{user.id}.png")

        wordcloud.to_file(path)

        return path

def setup(bot):
    bot.add_cog(Commands(bot))
