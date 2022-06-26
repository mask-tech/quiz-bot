import discord
from asyncio import sleep
from datetime import datetime
from discord.ext import commands
from os import chdir

chdir('\\'.join(__file__.split('\\')[:-1]))     #Changing path to keep files in same folder
quizbot = commands.Bot(command_prefix = '<>', intents = discord.Intents.all(), help_command = None)
quiz_progress = {}
token = '... not posting it here lol'
# server_id : {'participants' : [#list of participants] , 'status' : 0}

@quizbot.event
async def on_ready():
    print(f"Wake up time: {datetime.now()}")
    for guild in quizbot.guilds: 
        print(f"Up and running in server [{guild}]")
        try: open(f'logs/{guild.id}.txt', 'r+', encoding = 'utf-16').close()
        except IOError: open(f'logs/{guild.id}.txt', 'w', encoding = 'utf-16').close()

@quizbot.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == quizbot.user:
        if reaction.message.guild == None:
            #code for quiz...
            pass
        else:
            if reaction.message.content.startswith("**Starting Quiz ID:**"):
                if user != quizbot.user and reaction.emoji == '🇾':
                    quiz_progress[reaction.message.guild.id]['participants'].append(user.name)
                    print(f"Participant added: {user.name}")

@quizbot.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author == quizbot.user:
        if reaction.message.guild == None:
            #code for quiz...
            pass
        else:
            if reaction.message.content.startswith("**Starting Quiz ID:**"):
                if user != quizbot.user and reaction.emoji == '🇾':
                    quiz_progress[reaction.message.guild.id]['participants'].remove(user.name)
                    print(f"Participant removed: {user.name}")

@quizbot.event
async def on_message(message):
    if message.guild:
        with open(f'logs/{message.guild.id}.txt', 'a', encoding = 'utf-16') as file:
            file.write(f'[{message.author} | {message.author.id}]\n{message.content}\n\n')
    if message.author != quizbot.user and message.content.startswith(quizbot.command_prefix):
        try: 
            await quizbot.process_commands(message)
        except discord.ext.commands.errors.CommandNotFound: message.channel.send("Command does not exist. :-!")
    elif message.author == quizbot.user:
        if message.content.startswith("**Starting Quiz ID:**"):
            await message.add_reaction('🇾')


@quizbot.command(name = 'exit', aliases = ['kill', 'off', 'disconnect'])
async def exit(ctx):
    '''To turn off bot. Mainly for dev purposes. Won't be present in final one.'''
    print(f"Exit time: {datetime.now}")
    await quizbot.close()


@quizbot.command(name = 'start_quiz', aliases = ['start', 'begin', 'begin_quiz'])
async def start_quiz(ctx, quiz_id: int):
    '''Starts the quiz. Afterwards, another async function will be used to run the quiz'''
    quiz_progress[ctx.message.guild.id] = {'participants' : [] , 'status' : 0}
    await ctx.send(f"**Starting Quiz ID:** {quiz_id}. React with 🇾 to participate.")
    await sleep(10)

quizbot.run(token)
