from discord.ext import commands
from randomcolor import RandomColor
from typing import Callable, Generator
from wordcloud import WordCloud
import discord
import emoji as Emoji
import pathlib
import re
import sys

class Commands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True)
    async def id(self, ctx, *, user: discord.User = None):
        if user is None:
            user = ctx.message.author

        embed = discord.Embed()
        embed.title = "IDs"
        embed.description = f"IDs for {user.mention}."
        embed.colour = discord.Colour(self.getRandomColour())
        embed.add_field(name = "User:",
                        value = user.id,
                        inline = False)
        embed.add_field(name = "Current channel:",
                        value = ctx.message.channel.id,
                        inline = False)
        embed.add_field(name = "Current server:",
                        value = ctx.message.server.id,
                        inline = False)

        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(destination = ctx.message.channel,
                                    embed = embed)

        print(f"{ctx.message.author} retrieved IDs in "
              f"{ctx.message.server.name} #{ctx.message.channel.name}.")

    @commands.command(pass_context = True)
    async def react(self, ctx, emoji: str, limit: int = 100):
        await self.bot.delete_message(ctx.message)

        async def addReactions():
            async for message in self.bot.logs_from(ctx.message.channel, limit):
                await self.bot.add_reaction(message, emoji)

        if Emoji.get_emoji_regexp().fullmatch(emoji):
            await addReactions()
        else:
            pattern = re.compile(r"<:[a-zA-Z0-9_]+:([0-9]+)>$")
            match = pattern.fullmatch(emoji)

            if match:
                try:
                    emoji = self.getEmoji(match.group(1))
                except discord.InvalidArgument:
                    raise discord.InvalidArgument("Argument 'emoji' is not a valid custom emoji.")

                await addReactions()
            else:
                raise discord.InvalidArgument("Argument 'emoji' is not a valid Unicode emoji.")

        print(f"{ctx.message.author} reacted with {emoji} to {limit} messages "
              f"in {ctx.message.server.name} #{ctx.message.channel.name}.")

    @commands.command(pass_context = True)
    async def wc(self,
                 ctx,
                 user: discord.User = None,
                 channel: discord.Channel = None,
                 limit: int = 1000,
                 colour: str = None):
        if user is None:
            user = ctx.message.author

        if channel is None:
            channel = ctx.message.channel

        # Deletes the command message.
        await self.bot.delete_message(ctx.message)

        # Generates and posts a word cloud.
        imageFile = await self.getWordCloudImage(channel, user, limit, colour)
        await self.bot.send_file(ctx.message.channel, imageFile)
        pathlib.Path.unlink(imageFile)

        # Retrieves the word cloud attachment's URL.
        # def check(message: discord.Message) -> bool:
        #     if message.attachments:
        #         return dict(message.attachments[0])["filename"] == os.path.basename(imageFile)
        #
        #     return False
        #
        # imageMessage = await self.bot.wait_for_message(author = ctx.message.author,
        #                                                check = check)
        # imageURL = dict(imageMessage.attachments[0])["url"]
        # await self.bot.delete_message(imageMessage)

        # Embed properties.
        out = discord.Embed()
        out.title = "Word Cloud"
        out.description = f"Word cloud for {user.mention} in {channel.mention}."
        out.colour = discord.Colour(self.getRandomColour())
        # out.set_image(url = imageURL)

        await self.bot.send_message(destination = ctx.message.channel,
                                    embed = out)

        print(f"{ctx.message.author} generated a word cloud for {user} in "
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

        raise discord.InvalidArgument("Argument 'emojiID' does not reference a valid custom emoji.")

    async def getWordCloudImage(self,
                                channel: discord.Channel,
                                user: discord.User,
                                limit: int,
                                colour: str
                                ) -> pathlib.Path:
        def check(message: discord.Message) -> bool:
            return message.author == user

        text = await self.getContents(self.getMessages(channel, limit, check))
        wordcloud = WordCloud(width = 1280,
                              height = 720,
                              background_color = colour,
                              mode = "RGBA"
                              ).generate(text)

        path = pathlib.Path(sys.modules['__main__'].__file__).with_name("wc_temp")
        path.mkdir(parents = True, exist_ok = True)
        path = path.joinpath(f"wc_{user.id}.png")

        wordcloud.to_file(path)

        return path

def setup(bot):
    bot.add_cog(Commands(bot))
