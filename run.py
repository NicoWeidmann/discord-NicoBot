import logging
import sys
from bot import DemocracyBot
from votingbot import VotingCog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BotRunner")
bot = DemocracyBot()
bot.add_cog(VotingCog(bot))

if len(sys.argv) < 2:
    logger.error("""No bot token provided. Provide the bot token as first command line argument.
Alternatively, set bot.token and call bot.start().""")
else:
    bot.run(sys.argv[1])  # read bot token
