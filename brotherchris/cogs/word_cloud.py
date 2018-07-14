import io
import logging

from discord.ext import commands
from wordcloud import WordCloud as WC
import discord

from cogs import utils

class WordCloud:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.log: logging.Logger = logging.getLogger("bot.cogs.WordCloud")
        self.log.info("cogs.WordCloud loaded successfully.")

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
        text: str = await self.get_text(channel, user, limit)
        image: bytes = await self.generate_image(text, colour)
        await msg.channel.send(file=discord.File(image, filename=f"{user}.png"))

        # Embed properties.
        embed: discord.Embed = discord.Embed()
        embed.title = "Word Cloud"
        embed.description = \
            f"Word cloud for {user.mention} in {channel.mention}."
        embed.colour = discord.Colour(utils.get_random_colour())

        await msg.channel.send(embed=embed)
        self.log.info(
            f"{msg.author} generated a word cloud for {user} in "
            f"{channel.guild.name} #{channel.name}.")

    @staticmethod
    async def generate_image(text: str, colour: str) -> bytes:
        word_cloud: WC = WC(
            width=1280,
            height=720,
            background_color=colour,
            mode="RGBA"
            ).generate(text)

        with io.BytesIO() as bytestream:
            word_cloud.to_image().save(bytestream, format="PNG")
            return bytestream.getvalue()

    @staticmethod
    async def get_text(
            channel: discord.TextChannel,
            user: discord.User,
            limit: int
            ) -> str:
        msgs = utils.get_messages(channel, limit, lambda m: m.author == user)

        return "\n".join([m.content async for m in msgs])

def setup(bot: commands.Bot):
    bot.add_cog(WordCloud(bot))
