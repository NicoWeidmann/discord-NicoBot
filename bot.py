from discord.ext import commands
import logging


class DemocracyBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='!', description="A democratic discord bot.")
        self._logger = logging.getLogger("VotingBot")

        def on_ready():
            self._logger.info('Sucessfully logged in as {0.user.name} with ID {0.user.id}.'.format(self))
