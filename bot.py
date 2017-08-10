import discord
import logging
from asyncio import ensure_future
from commands import *


class Bot:

    def __init__(self, client):
        self._client = client
        self._votings = {}
        self._commands = [StartVoting(), AddVote(), EvaluateVoting()]
        self._logger = logging.getLogger("VotingBot")

        @self._client.event
        async def on_ready():
            self._logger.info('Nice. Sucessfully logged in as {0.user.name} with ID {0.user.id}.'.format(self._client))

        @self._client.event
        async def on_message(message):

            for command in self._commands:
                if command.hasCorrectArguments(message):
                    command.execute(self, message)

    def start(self):
        self._client.run(self.token)

    def setToken(self, token):
        self.token = token

    def createVoting(self, owner, channel, uid, question, answers):

        if not 0 <= len(uid) <= 4:
            raise IllegalUID

        if len(answers) < 2:
            raise NotEnoughAnswers

        if uid in self._votings:
            raise DuplicateUID

        voting = Voting(owner, channel, uid, question, answers)
        self._votings[uid] = voting

        self._logger.info("Created Voting with ID {0.uid} for owner {0.owner.name} (ID: {0.owner.id})".format(voting))

    def vote(self, voter, uid, vote):
        if uid not in self._votings:
            raise IllegalUID

        voting = self._votings[uid]

        if not 0 <= vote < len(voting.answers):
            raise IllegalVote

        voting.addVote(voter, vote)

        self._logger.info("Added vote for Voting with ID {0.uid} from user {1.name} (ID: {1.id})".format(voting, voter))

    def evaluate(self, sender, uid):
        if uid not in self._votings:
            raise IllegalUID

        voting = self._votings[uid]
        voting.disable()
        ensure_future(self._client.send_message(voting.channel, voting.evaluate()))
        self._logger.info("Evaluated Voting with ID {0.uid}. Thank you for using VoteBot.".format(voting))


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
            raise DuplicateVote
        elif not self.active:
            raise ExpiredVoting
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
