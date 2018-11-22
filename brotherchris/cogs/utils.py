import json
from typing import AsyncGenerator, Callable, Dict

import discord
from randomcolor import RandomColor


def load_config(prop: str) -> Dict:
    """
    Retrieves the configuration for the given property as a
    :class:`dictionary<dict>` from Configuration.json.

    Parameters
    ----------
    prop: str
        The name of the property for which to retrieve the configuration.

    Returns
    -------
    Dict
        The configuration for the given property.
    """
    with open('Configuration.json') as file:
        return json.load(file)[prop]


def get_random_colour() -> int:
    """
    Generates a random colour as a hexadecimal integer.

    Notes
    -------
    The :module:`randomcolor` library is used to generate a random colour in hex
    format. The '#' character is stripped from the string and then then string
    is converted to a hexadecimal integer.

    Returns
    -------
    Int
        A random colour represented as a hexadecimal integer.
    """
    return int(RandomColor().generate()[0].lstrip('#'), 16)


async def get_messages(
    channel: discord.TextChannel,
    limit: int,
    check: Callable[[discord.Message], bool] = None
) -> AsyncGenerator[discord.Message, None]:
    counter = 0
    history_limit = 1000

    if limit > history_limit:
        history_limit = limit

    async for message in channel.history(limit=history_limit):
        if (check is None or check(message)) and counter != limit:
            counter += 1
            yield message
