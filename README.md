# discord-DemocracyBot
Hi, I am DemocracyBot, a very simple [Discord](https://discordapp.com) Bot.  
My only feature and purpose is to deliver democracy to all the discord servers.
I facilitate this by providing an easy-to-use interface for creating and evaluating votes:

* `!createvote <uid> <question> [answers...]` creates a new voting with a question and some possible answers
* `!vote <uid> <answer>` votes on a previously created voting
* `!evaluate <uid>` counts the votes and shows them in a beautifully crafted response

For more information on my commands, have a peek at my `!help` command.

---

### For the nerds

The bot was written in Python using [discord.py](https://github.com/Rapptz/discord.py), the Discord API wrapper for Python.

If you want to run the bot, clone this repository and make sure to install the discord.py library:
```
python3 -m pip install -U discord.py
```
after this, simply start the bot:
```
python3 run.py <YOUR BOT TOKEN>
```

You can add additional functionality by adding more cogs to the bot. The best place to do this is the `run.py` file.
