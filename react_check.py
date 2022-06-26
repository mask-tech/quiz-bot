import discord
from discord.ext import commands
from datetime import datetime
from os import chdir

chdir('\\'.join(__file__.split('\\')[:-1]))     #Changing path to keep files in same folder
quizbot = commands.Bot(command_prefix = '<>', intents = discord.Intents.all(), help_command = None)

@quizbot.event
async def on_ready():
    print(f"Wake up time: {datetime.now()}")
    for guild in quizbot.guilds: 
        print(f"Up and running in server [{guild}]")
        try: open(f'logs/{guild.id}.txt','r+').close()
        except IOError: open(f'logs/{guild.id}.txt','w').close()

@quizbot.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == quizbot.user:
        if reaction.message.guild == None:
            #code for quiz...
            pass
        else:
            #code for quiz entry
            pass

@quizbot.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author == quizbot.user:
        if reaction.message.guild == None:
            #code for quiz...
            pass
        else:
            #code for quiz entry
            pass

@quizbot.event
async def on_message(message):
    if message.guild:
        with open(f'logs/{message.guild.id}.txt', 'a') as file:
            file.write(f'[{message.author} | {message.author.id}]\n{message.content}\n\n')
    if message.author != quizbot.user and message.content.startswith(quizbot.command_prefix):
        try: 
            await quizbot.process_commands(message)
        except discord.ext.commands.errors.CommandNotFound: message.channel.send("Command does not exist. :-!")


@quizbot.command(name = 'exit', aliases = ['kill', 'off', 'disconnect'])
async def exit(ctx):
    '''To turn off bot. Mainly for dev purposes. Won't be present in final one.'''
    print(f"Exit time: {datetime.now}")
    await quizbot.close()

quizbot.run('OTY5NDU0MTQzMjA5MDc4ODM0.Ymtohw.YiP4otT8_srI_ghKtQKMOSoEdUE')