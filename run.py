import logging
import sys
from bot import DemocracyBot
from cogs.votingbot import Voting
from cogs.pythonbot import Python

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BotRunner")
bot = DemocracyBot()
bot.add_cog(Voting(bot))
bot.add_cog(Python(bot))

if len(sys.argv) < 2:
    logger.error("""No bot token provided. Provide the bot token as first command line argument.
Alternatively, call bot.run(<token>).""")
else:
    bot.run(sys.argv[1])  # read bot token
