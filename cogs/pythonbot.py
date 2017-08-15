import logging
from discord.ext import commands
import discord
import asyncio
import code
import sys
from io import StringIO


class DiscordInterpreter(code.InteractiveInterpreter):

    def __init__(self, stdout, stderr):
        super().__init__()
        self._stdout = stdout
        self._stderr = stderr

    def runcode(self, code):
        """Execute a code object.
        When an exception occurs, self.showtraceback() is called to
        display a traceback.  All exceptions are caught, including
        SystemExit.
        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        stdout and stderr are redirected.
        """
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        # redirect output streams
        redirected_stdout = sys.stdout = StringIO()
        redirected_stderr = sys.stderr = StringIO()
        try:
            exec(code, self.locals)
        except:
            self.showtraceback()
        finally:
            # restore output streams
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        # propagate printed content
        stdout = redirected_stdout.getvalue()
        stderr = redirected_stderr.getvalue()

        if stdout is not "":
            self._stdout(stdout)
        if stderr is not "":
            self._stderr(stderr)

    def write(self, data):
        """
        Write a string to the stderr stream.
        """
        self._stderr(data)


class Python:

    logger = logging.getLogger("Python_Cog")

    def _send_stdout(self):
        def send(out):
            asyncio.ensure_future(self.bot.say("Interpreter Output:\n```\n" + out + "\n```"))
        return send

    def _send_stderr(self):
        def send(err):
            asyncio.ensure_future(self.bot.say("Interpreter Error Output:\n```\n" + err + "\n```"))
        return send

    def __init__(self, bot):
        self.bot = bot
        self._interpreter = DiscordInterpreter(self._send_stdout(), self._send_stderr())

    @commands.command(name="reset")
    async def reset(self):
        """
        Resets the python interpreter.
        """
        self._interpreter = DiscordInterpreter(self._send_stdout(), self._send_stderr())

    @commands.command(name="exec")
    async def execute(self, *, command):
        """
        Executes a python instruction.

        command - the instruction to execute

        If you want to execute a multi line instruction, do it like in this example:

        !exec
        def foo():
            print('bar')

        Please note that as of now, no "double quotes" are supported.
        """
        command += "\n"
        if self._interpreter.runsource(command):
            await self.bot.say("*Incomplete instruction.*")
