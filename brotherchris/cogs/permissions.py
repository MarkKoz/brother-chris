from enum import Enum
from typing import Dict, List, NamedTuple
import logging

from discord.ext import commands
import discord

from cogs import utils

log: logging.Logger = logging.getLogger(__name__)

class Category(Enum):
    GENERAL: int = discord.Permissions().general().value
    TEXT: int = discord.Permissions().text().value
    VOICE: int = discord.Permissions().voice().value

class Permission(NamedTuple):
    name: str
    value: bool
    category: Category

class Permissions:
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.config: Dict = utils.load_config("Permissions")

    @commands.command()
    @commands.guild_only()
    async def perms(
            self,
            ctx: commands.Context,
            user: discord.User = None,
            channel: discord.TextChannel = None):
        msg: discord.Message = ctx.message

        if user is None:
            user = msg.author

        if channel is None:
            channel = msg.channel

        # Deletes the command message.
        await msg.delete()

        perms: List[Permission] = self.get_list(
            msg.channel.permissions_for(msg.author))

        if self.config["justify"]:
            width: int = self.get_max_width(perms, self.config["padding"])
        else:
            width: int = 0

        embed: discord.Embed = discord.Embed()
        embed.colour = discord.Colour(utils.get_random_colour())
        embed.title = "Member Permissions"
        embed.description = \
            f"Permissions for {user.mention} in {channel.mention}."

        embed.add_field(
            name="General Permissions",
            value=self.get_string(perms, Category.GENERAL, width),
            inline=False)
        embed.add_field(
            name="Text Permissions",
            value=self.get_string(perms, Category.TEXT, width),
            inline=False)
        embed.add_field(
            name="Voice Permissions",
            value=self.get_string(perms, Category.VOICE, width),
            inline=False)

        await msg.channel.send(embed=embed)
        log.info(
            f"{msg.author} retrieved {user}'s permissions for #{channel.name} "
            f"in {msg.guild.name} #{msg.channel.name}.")

    @staticmethod
    def get_list(perms: discord.Permissions) -> List[Permission]:
        lst: List[Permission] = []

        # Iterates through every permission. perm is the name of the
        # permission's respective attribute in discord.Permissions.
        for perm, value in perms:
            # Creates a Permissions object with no bits set for the purpose of
            # comparison.
            p: discord.Permissions = discord.Permissions().none()

            # Updates the bit that corresponds to the current permission in the
            # loop iteration.
            p.update(**{perm: True})

            # Iterates through every permission category.
            cat: Category
            for cat in Category:
                # Compares the value of the enum, which is the raw bit array
                # field of the permission category, against the bit of the
                # comparison object. If the bit is set in both objects, then the
                # current category is the permission's category.
                if cat.value & p.value != 0:
                    lst.append(Permission(perm, value, cat))

        return lst

    @staticmethod
    def get_string(
            perms: List[Permission],
            category: Category,
            width: int) -> str:
        return "".join(
            f"{p.name.ljust(width)} `{p.value}`\n"
            for p in perms if p.category == category)

    @staticmethod
    def get_max_width(perms: List[Permission], padding: int) -> int:
        return max(len(p.name) for p in perms) + padding

def setup(bot: commands.Bot):
    bot.add_cog(Permissions(bot))
