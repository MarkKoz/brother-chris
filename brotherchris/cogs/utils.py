from randomcolor import RandomColor
from typing import Dict
import json

def loadConfig(prop: str) -> Dict:
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
    with open("Configuration.json") as file:
        return json.load(file)[prop]

def getRandomColour() -> int:
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
