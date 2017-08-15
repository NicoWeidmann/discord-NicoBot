from discord.ext import commands
import logging
import asyncio


class DemocracyBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='!', description="A democratic discord bot.")
        self.logger = logging.getLogger("DemocracyBot")

    @asyncio.coroutine
    def on_ready(self):
        self.logger.info('Sucessfully logged in as {0.user.name} with ID {0.user.id}.'.format(self))
