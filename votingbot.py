import logging
from discord.ext import commands
import asyncio

logger = logging.getLogger("Voting_Cog")


class VotingCog:

    def __init__(self, bot):
        self._logger = logger

        self.bot = bot
        self._votings = {}

    @commands.command(name="test", pass_context=True)
    @asyncio.coroutine
    def test(self, ctx, *params):
        for param in params:
            print(param)

    @commands.command(name="createvote", pass_context=True)
    @asyncio.coroutine
    def createVote(self, ctx, uid, question, *answers):

        if not 0 <= len(uid) <= 4:
            raise VotingException("the voting ID can only contain 4 characters")

        if len(answers) < 2:
            raise VotingException("a voting has to provide at least 2 answers")

        if uid in self._votings:
            raise VotingException("a voting with the ID {0} already exists".format(uid))

        voting = Voting(ctx.message.author, ctx.message.channel, uid, question, answers)
        self._votings[uid] = voting

        self._logger.info("Created Voting with ID {0.uid} for owner {0.owner.name} (ID: {0.owner.id})".format(voting))

    @commands.command(name="vote", pass_context=True)
    @asyncio.coroutine
    def vote(self, ctx, uid, vote):

        if uid not in self._votings:
            raise VotingException("a voting with the ID {0} does not exist".format(uid))

        voting = self._votings[uid]
        vote = int(vote)

        if not 0 <= vote < len(voting.answers):
            raise VotingException("{0} is not a valid answer to this question".format(vote))

        voter = ctx.message.author
        voting.addVote(voter, vote)

        self._logger.info("Added vote for Voting with ID {0.uid} from user {1.name} (ID: {1.id})".format(voting, voter))

    @commands.command(name="evaluate", pass_context=True)
    @asyncio.coroutine
    def evaluate(self, ctx, uid):

        if uid not in self._votings:
            raise VotingException("a voting with the ID {0} does not exist".format(uid))

        voting = self._votings[uid]

        if ctx.message.author is not voting.owner:
            raise VotingException("the author is not allowed to evaluate this voting")

        voting.disable()
        yield from self.bot.say(voting.evaluate())
        self._logger.info("Evaluated Voting with ID {0.uid}. Thank you for using VoteBot.".format(voting))

    @commands.command(name="showvote", pass_context=True)
    @asyncio.coroutine
    def showVote(self, ctx, uid):

        if uid not in self._votings:
            raise VotingException("a voting with the ID {0} does not exist".format(uid))

        yield from self.bot.say(self._votings[uid].printVote(ctx))

    @createVote.error
    @vote.error
    @evaluate.error
    @showVote.error
    @asyncio.coroutine
    def command_error(self, error, context):
        """
        Reads out the exception's message, if the exception is an
        instance of VotingException.
        """

        if not isinstance(error, VotingException):
            logger.info("ignored an exception")
            return

        yield from self.bot.say("Oops, " + error.message, delete_after=10)


class Voting:

    def __init__(self, owner, channel, uid, question, answers):
        self.owner = owner
        self.channel = channel
        self.uid = uid
        self.question = question
        self.answers = answers
        self.votes = dict()
        self.active = True

    def addVote(self, voter, answer):
        """
        Adds a new vote to the voting.

        Args:
            voter: The discord user that voted.
            answer: The index of the answer the voter voted for.
        """

        if voter.id in self.votes:
            # voter has already voted
            raise VotingException("voter has already voted")
        elif not self.active:
            raise VotingException("the voting is inactive")
        elif not 0 <= answer < len(self.answers):
            raise VotingException("[{0}] is not a valid answer to this question".format(answer))
        else:
            self.votes[voter.id] = answer

    def evaluate(self):
        """
        Evaluates the voting and sends a message with the results.
        """
        msg = "Hello there. Here is your evaluation on the vote:\n\n[{0}] **{1}**\n".format(self.uid, self.question)

        totalVotes = len(self.votes)
        for i, v in enumerate(self.answers):
            currentVotes = list(self.votes.values()).count(i)
            percentage = currentVotes / totalVotes * 100 if totalVotes != 0 else 0
            msg = msg + v + ": {0:.2f}".format(percentage) + '%\n'

        return msg

    def disable(self):
        self.active = False

    def printVote(self, ctx):
        msg = "{0.owner.name} created the following voting:\n[{0.uid}] **{0.question}**".format(self)

        for i, answer in enumerate(self.answers):
            msg += "\n[{0}] {1}".format(i, answer)

        msg += "\n\nTo vote, type {0}vote {1} <answer>".format(ctx.prefix, self.uid)
        return msg


class VotingException(commands.CommandError):

    def __init__(self, message):
        self.message = message
