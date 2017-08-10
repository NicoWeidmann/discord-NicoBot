import re


class Command:

    commandSymbol = "!"

    def matches(self, input):
        return input.content.startswith(Command.commandSymbol + self.getCmd())


class StartVoting(Command):

    pattern = re.compile(Command.commandSymbol + "createvote (\S+) \"([^\"]+)\" ((?:\"[^\"]+\" )*\"[^\"]+\")")

    def getCmd(self, input):
        return "createvote"

    def hasCorrectArguments(self, input):
        return StartVoting.pattern.match(input.content) is not None

    def execute(self, bot, input):
        match = StartVoting.pattern.match(input.content)

        if not self.hasCorrectArguments(input):
            # incorrect arguments
            return

        uid = match.group(1)
        question = match.group(2)
        # filter answers from split
        answers = [i for i in match.group(3).split("\"") if len(i) > 0 and i != ' ']

        bot.createVoting(input.author, input.channel, uid, question, answers)


class AddVote(Command):

    pattern = re.compile(Command.commandSymbol + "vote (\S+) (\d+)")

    def getCmd(self):
        return "vote"

    def hasCorrectArguments(self, input):
        return AddVote.pattern.match(input.content) is not None

    def execute(self, bot, input):
        match = AddVote.pattern.match(input.content)

        if not self.hasCorrectArguments(input):
            # incorrect arguments
            return

        bot.vote(input.author, match.group(1), int(match.group(2)))


class EvaluateVoting(Command):

    pattern = re.compile(Command.commandSymbol + "evaluate (\S+)")

    def getCmd(self):
        return "evaluate"

    def hasCorrectArguments(self, input):
        return EvaluateVoting.pattern.match(input.content) is not None

    def execute(self, bot, input):
        if not self.hasCorrectArguments(input):
            # incorrect arguments
            return

        bot.evaluate(input.author, EvaluateVoting.pattern.match(input.content).group(1))
