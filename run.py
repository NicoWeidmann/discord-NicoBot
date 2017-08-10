import logging
import discord
import sys
from bot import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BotRunner")
bot = Bot(discord.Client())

if len(sys.argv) < 2:
    logger.error("""No bot token provided. Provide the bot token as first command line argument.
Alternatively, set bot.token and call bot.start().""")
else:
    bot.token = sys.argv[1]  # read bot token
    bot.start()
