from discord.ext import commands
from typing import Dict
import discord
import logging

import cogs.Utils as Utils

class Permissions:
    def __init__(self, bot):
        self.bot = bot
        self.log = logging.getLogger("bot.cogs.Permissions")
        self.log.info("cogs.Permissions loaded successfully.")
        self.config = Utils.loadConfig("Permissions")

    @commands.command(pass_context = True)
    async def perms(self,
                    ctx,
                    user: discord.User = None,
                    channel: discord.Channel = None):
        msg = ctx.message

        if user is None:
            user = msg.author

        if channel is None:
            channel = msg.channel

        # Deletes the command message.
        await self.bot.delete_message(msg)

        perms = {"General": self.getDict(discord.Permissions().general()),
                 "Text": self.getDict(discord.Permissions().text()),
                 "Voice": self.getDict(discord.Permissions().voice())
                 } # type: Dict[str, Dict[str, bool]]

        if self.config["justify"]:
            width = self.getWidthMax(perms, self.config["padding"])
        else:
            width = 0

        embed = discord.Embed()
        embed.colour = discord.Colour(Utils.getRandomColour())
        embed.title = "Member Permissions"
        embed.description = f"Permissions for {user.mention} in {channel.mention}."

        embed.add_field(name = "General Permissions",
                        value = self.getString(perms, "General", width),
                        inline = False)

        embed.add_field(name = "Text Permissions",
                        value = self.getString(perms, "Text", width),
                        inline = False)

        embed.add_field(name = "Voice Permissions",
                        value = self.getString(perms, "Voice", width),
                        inline = False)

        await self.bot.send_message(destination = msg.channel, embed = embed)
        self.log.info(f"{msg.author} retrieved {user}'s permissions for "
                      f"#{channel.name} in {msg.server.name} "
                      f"#{msg.channel.name}.")

    @staticmethod
    def getDict(perms: discord.Permissions) -> Dict[str, bool]:
        d = {} # type: Dict[str, bool]

        for perm, value in perms:
            if value:
                d[perm] = value

        return d

    @staticmethod
    def getString(perms: Dict[str, Dict[str, bool]],
                  category: str,
                  width: int) -> str:
        print(f"Width: {width}")
        # Avoids appending newline to first item.
        key, value = perms[category].popitem()
        # string = f"{key} `{value}`"
        string = f"{key.ljust(width)} `{value}`"

        for key, value in perms[category].items():
            string += f"\n{key.ljust(width)} `{value}`"

        return string

    @staticmethod
    def getWidthMax(d: Dict[any, Dict[str, any]], padding: int) -> int:
        return max(len(key) for value in d.values()
                   for key in value.keys()) + padding

def setup(bot):
    bot.add_cog(Permissions(bot))
