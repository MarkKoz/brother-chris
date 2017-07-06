from randomcolor import RandomColor
import json

def loadConfig(prop: str):
    with open("Configuration.json") as file:
        return json.load(file)[prop]

def getRandomColour() -> int:
    return int(RandomColor().generate()[0].lstrip('#'), 16)
