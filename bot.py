from discord.ext import commands
import logging
import asyncio


class DemocracyBot(commands.Bot):

    description = """A democratic discord bot.
                     Please report bugs and missing features to
                     https://github.com/NicoWeidmann/discord-DemocracyBot/issues"""

    def __init__(self):
        super().__init__(command_prefix='!', description=DemocracyBot.description)
        self.logger = logging.getLogger("DemocracyBot")

    @asyncio.coroutine
    def on_ready(self):
        self.logger.info('Sucessfully logged in as {0.user.name} with ID {0.user.id}.'.format(self))
