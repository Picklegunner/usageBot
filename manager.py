import discord
from discord.ext import commands
from collections import defaultdict
import data
import operator
import re
import math

TOKEN = ''


description = '''Discord analysis and statistics bot'''

bot = commands.Bot(command_prefix='!', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
async def match_all(ctx, expression, *args):
    """Message matching using regex
        v - verbose <INCOMPLETE>
        i - ignore commands, adds common bot prefixes to start of regex"""

    flags = {}
    flags['v'] = 'v' in args
    flags['i'] = 'i' in args

    user_matches = defaultdict(int)
    user_matched_messages = defaultdict(int)
    user_messages = defaultdict(int)

    regex = re.compile(expression)

    channels = []
    location = ""  #TODO let users pass in keyword arguments

    try:
        channels = kwargs['c']
        location = str(kwargs['c'])
    except Exception:
        channels = ctx.message.server.channels
        location = ctx.message.server.name

    try:
        for channel in channels:
            async for message in bot.logs_from(channel, limit=1000000):
                if (message.author.id == bot.user.id) and ('i' in args):
                    continue
                elif flags['i'] and message.content[:1] in ['!','?','`','~']:
                    continue
                user_messages[message.author.name] += 1
                match = len(regex.findall(message.content))
                if match != 0:
                    user_matches[message.author.name] += match
                    user_matched_messages[message.author.name] += 1

    except Exception as e:
        await bot.say("Exception " + str(e) + "!")
    else:

            # sums maximum var lengths for formatting purposes
        name_len = 0
        match_len = 0
        message_len = 0

        if user_matches:
            for (u,c) in user_matches.items():
                name_len = max(name_len, len(u))
                match_len = max(match_len, c)
            match_len = math.ceil(math.log(match_len,10))

        if user_messages:
            for (u,c) in user_messages.items():
                message_len = max(message_len, c)
            message_len = math.ceil(math.log(message_len,10))

        if flags['v']:
            total_matches = 0
            if user_matches:
                for (u,c) in user_matches.items():
                    total_matches += c

            total_messages = 0
            if user_messages:
                for (u,c) in user_messages.items():
                    total_messages += c
            
            output = "```Matches for /{}/ in \'{}\': {}\n".format(regex.pattern, location, total_matches)
            user_matches = sorted(user_matches.items(), key=operator.itemgetter(1))
            user_matches.reverse()
            if user_matches: #Make sure matches were found
                for (user, user_match) in user_matches:
                    output += "> {:<{name_len}} | {:>{match_len}} matches in {:>{message_len}} messages, {:6.2f}% personal | {:6.2f}% server(messages) | {:6.2f}% server(matches) \n".format(
                        user,
                        user_match,
                        user_messages[user],
                        (100.0*user_matched_messages[user])/user_messages[user],
                        (100.0*user_matched_messages[user])/total_messages,
                        (100.0*user_match)/total_matches,
                        name_len=name_len,
                        match_len=match_len,
                        message_len=message_len)
                output += "```"
            else:
                output += "No matches found!\n```"
            await bot.say(output)
        else:
            output = "```Matches for /{}/ in \'{}\'\n".format(regex.pattern, location)
            user_matches = sorted(user_matches.items(), key=operator.itemgetter(1))
            user_matches.reverse()
            if user_matches: #Make sure matches were found
                for (user, user_match) in user_matches:
                    output += "> {:<{name_len}} | {:>{match_len}} matches in {:>{message_len}} messages\n".format(
                        user,
                        user_match,
                        user_messages[user],
                        name_len=name_len,
                        match_len=match_len,
                        message_len=message_len)
                output += "```"
            else:
                output += "No matches found!"
            await bot.say(output)



@bot.command(pass_context=True)
async def count(ctx, *args, **kwargs):
    """Counts total messages in server
        v - verbose
        c=['channel1','channel2'] - limit to specific channel <INCOMPLETE>"""

    try:
        counter = 0
        user_messages = defaultdict(int)
        channels = []
        location = ""  #TODO let users pass in keyword arguments
        try:
            channels = kwargs['c']
            location = str(kwargs['c'])
        except Exception:
            channels = ctx.message.server.channels
            location = ctx.message.server.name


        if 'v' in args:
            for channel in channels:
                async for message in bot.logs_from(channel, limit=1000000):
                    counter += 1
                    user_messages[message.author.name] += 1
        else:
            for channel in channels:
                async for message in bot.logs_from(channel, limit=1000000):
                    counter += 1

    except Exception as e:
        await bot.say("Exception " + str(e) + "!")
    else:
        if 'v' in args:
            output = "```Total messages in \'{}\' | {}\n".format(location, counter)
            user_messages = sorted(user_messages.items(), key=operator.itemgetter(1))
            user_messages.reverse()
            for (user, user_count) in user_messages:
                output += "> {} : {}\n".format(user, user_count)
            output += "```"
            await bot.say(output)
        else:
            await bot.say("```Total messages in \'{}\' | {}```".format(location, counter))



bot.run(TOKEN)