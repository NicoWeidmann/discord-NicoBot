import logging
from discord.ext import commands
import discord
import asyncio

logger = logging.getLogger("Voting_Cog")


class Voting:

    def __init__(self, bot):
        self._logger = logger
        self.bot = bot
        self._votings = {}

    @commands.command(name="createvote", pass_context=True, no_pm=True)
    @asyncio.coroutine
    def createVote(self, ctx, uid, question, *answers):
        """
        Create a new vote.

        uid      - the unique id of the voting
        question - the question you want to vote on
        answers  - the possible answers to the question

        Make sure to put the question and each answer in quotes if they contain spaces!
        """

        if not 0 <= len(uid) <= 4:
            raise VotingException("the voting ID can only contain 4 characters")

        if len(answers) < 2:
            raise VotingException("you have to provide at least 2 answers")

        if uid in self._votings:
            raise VotingException("a voting with the ID {0} already exists".format(uid))

        voting = Voting_Model(ctx.message.author, ctx.message.channel, uid, question, answers)
        self._votings[(uid, ctx.message.server.id)] = voting

        self._logger.info("Created Voting with ID {0.uid} for owner {0.owner.name} (ID: {0.owner.id})".format(voting))

    @commands.command(name="vote", pass_context=True, no_pm=True)
    @asyncio.coroutine
    def vote(self, ctx, uid, vote):
        """
        Vote on on a voting.

        uid  - the unique id of the voting
        vote - the number of the answer you want to vote for

        You can only vote once per voting.
        """

        if (uid, ctx.message.server.id) not in self._votings:
            raise VotingException("a voting with the ID {0} does not exist".format(uid))

        voting = self._votings[(uid, ctx.message.server.id)]
        vote = int(vote)

        if not 0 <= vote < len(voting.answers):
            raise VotingException("{0} is not a valid answer to this question".format(vote))

        voter = ctx.message.author
        voting.addVote(voter, vote)

        self._logger.info("Added vote for Voting with ID {0.uid} from user {1.name} (ID: {1.id})".format(voting, voter))

    @commands.command(name="evaluate", pass_context=True, no_pm=True)
    @asyncio.coroutine
    def evaluate(self, ctx, uid):
        """
        Evaluates a voting.

        uid - the unique id of the voting

        Only the owner of the voting can evaluate it.
        Once the voting is evaluated, no additional votes will be counted.
        """

        if (uid, ctx.message.server.id) not in self._votings:
            raise VotingException("a voting with the ID {0} does not exist".format(uid))

        voting = self._votings[(uid, ctx.message.server.id)]

        if ctx.message.author is not voting.owner:
            raise VotingException("only the author ({0}) is allowed to evaluate this voting".format(voting.owner.name))

        yield from self.bot.say(voting.evaluate())

        @asyncio.coroutine
        def deleteVote():
            yield from asyncio.sleep(300, loop=self.bot.loop)
            if (uid, ctx.message.server.id) in self._votings and not voting.active:
                del self._votings[(uid, ctx.message.server.id)]
                self._logger.info("Deleted Voting with ID {0} on server with ID {1}".format(uid, ctx.message.server.id))

        # schedule deletion of this voting
        discord.compat.create_task(deleteVote(), loop=self.bot.loop)

        self._logger.info("Evaluated Voting with ID {0.uid}. Thank you for using VoteBot.".format(voting))

    @commands.command(name="showvote", pass_context=True, no_pm=True)
    @asyncio.coroutine
    def showVote(self, ctx, uid):
        """
        Shows information on a voting.
        This command prints a summary of the voting with the possible answers.
        """

        if (uid, ctx.message.server.id) not in self._votings:
            raise VotingException("a voting with the ID {0} does not exist".format(uid))

        yield from self.bot.say(self._votings[(uid, ctx.message.server.id)].printVote(ctx))

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
            logger.warning("ignored an exception")
            return

        yield from self.bot.say("Oops, " + error.message, delete_after=10)


class Voting_Model:

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
            raise VotingException("you have already voted on this voting")
        elif not self.active:
            raise VotingException("the voting has already been evaluated")
        elif not 0 <= answer < len(self.answers):
            raise VotingException("[{0}] is not a valid answer to this question".format(answer))
        else:
            self.votes[voter.id] = answer

    def evaluate(self):
        """
        Evaluates the voting and sends a message with the results.
        """

        if not self.active:
            raise VotingException("this vote has already been evaluated.")

        return self.buildEvaluationMsg()

    def buildEvaluationMsg(self):
        msg = "Hello there. Here is your evaluation on the vote:\n\n[{0}] **{1}**\n\n".format(self.uid, self.question)

        totalVotes = len(self.votes)
        for a, v in sorted([(a, list(self.votes.values()).count(i)) for i, a in enumerate(self.answers)],
                           key=lambda tup: -tup[1]):
            percentage = v / totalVotes if totalVotes != 0 else 0
            bar_length = int(percentage * 25)
            msg = (msg + a + ":\n" +
                   "     `[" + "#"*bar_length + " "*(25-bar_length) + "]` {0:.2f}".format(percentage * 100) + '%\n')

        self.disable()
        return msg

    def disable(self):
        self.active = False

    def printVote(self, ctx):

        if not self.active:
            raise VotingException("this vote has already been evaluated:\n\n" + self.buildEvaluationMsg())

        msg = "{0.owner.name} created the following voting:\n[{0.uid}] **{0.question}**".format(self)

        for i, answer in enumerate(self.answers):
            msg += "\n[{0}] {1}".format(i, answer)

        msg += "\n\nTo vote, type {0}vote {1} <answer>".format(ctx.prefix, self.uid)
        return msg


class VotingException(commands.CommandError):

    def __init__(self, message):
        self.message = message
