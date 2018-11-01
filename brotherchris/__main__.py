import logging

from brotherchris.bot import BrotherChris
from brotherchris.cogs import utils

log: logging.Logger = logging.getLogger("brotherchris")
config: dict = utils.load_config("Bot")
bot = BrotherChris()

for extension in config["extensions"]:
    try:
        bot.load_extension(extension)
        log.info(f"{extension} loaded successfully.")
    except Exception as e:
        log.error(f"{extension} failed to load.\n{type(e).__name__}: {e}")

bot.run(config["token"])
