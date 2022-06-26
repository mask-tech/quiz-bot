import discord, json
from asyncio import sleep
from datetime import datetime
from discord.ext import commands
from os import chdir

chdir('\\'.join(__file__.split('\\')[:-1]))     #Changing path to keep files in same folder
quizbot = commands.Bot(command_prefix = '<>', intents = discord.Intents.all(), help_command = None)
quiz_progress = {}
loaded_quizzes = {}
responses = {}

with open('\\'.join(__file__.split('\\')[:-2])+'\\token.txt') as file: token = file.read()

def format_question(guild_id: int, question: dict):
    return f"**Quiz ID:** {guild_id} | {quiz_progress[guild_id]['quiz_id']}\n__**Sauce:**__ {question['sauce']}\n__**Text:**__ {question['text']}\n"+'\n'.join([f"{i} {question['options'][i]}" for i in question['options']])

async def quiz_refresh(guild_id):
    '''Main quiz work is done here.'''
    for user in quiz_progress[guild_id]['participants']:
        await user.send(f"You have been registered for **Quiz {quiz_progress[guild_id]['quiz_id']}** in server **{quizbot.get_guild(guild_id)}**")
        with open(f'quizzes/{quiz_progress[guild_id]["quiz_id"]}.json', encoding = 'utf-16') as file:
            loaded_quizzes[guild_id] = json.load(file)
        await quiz_progress[guild_id]['channel'].send("**Participants of the quiz:\n**" + '\n'.join([f'<@{user.id}>' for user in quiz_progress[guild_id]['participants']])+"\nQuiz will start in 5 seconds.")
        await sleep(5)
    quiz_progress[guild_id]['status'] = 1
    while quiz_progress[guild_id]['status'] <= loaded_quizzes[guild_id]['quiz_length']:
        message_string = format_question(guild_id, loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1])
        for user in quiz_progress[guild_id]['participants']:
            await user.send(message_string)
            await sleep(15)
        quiz_progress[guild_id]['status'] += 1
    else:
        quiz_progress.pop(guild_id)

@quizbot.event
async def on_ready():
    print(f"Wake up time: {datetime.now()}")
    for guild in quizbot.guilds: 
        print(f"Up and running in server [{guild}]")
        try: open(f'logs/{guild.id}.txt', 'r+', encoding = 'utf-16').close()
        except IOError: open(f'logs/{guild.id}.txt', 'w', encoding = 'utf-16').close()
        quiz_progress[guild.id] = None

@quizbot.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == quizbot.user:
        if reaction.message.guild == None:
            #code for quiz...
            pass
        else:
            if reaction.message.content.startswith("**Starting Quiz ID:**"):
                if user != quizbot.user and reaction.emoji == '🇾' and quiz_progress[reaction.message.guild.id]['status']==0 and reaction.message.id == quiz_progress[reaction.message.guild.id]['message_id']:
                    quiz_progress[reaction.message.guild.id]['participants'].append(user)
                    print(f"Participant added: {user.name}")

@quizbot.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author == quizbot.user:
        if reaction.message.guild == None:
            #code for quiz...
            pass
        else:
            if reaction.message.content.startswith("**Starting Quiz ID:**"):
                if user != quizbot.user and reaction.emoji == '🇾' and quiz_progress[reaction.message.guild.id]['status']==0 and reaction.message.id == quiz_progress[reaction.message.guild.id]['message_id']:
                    quiz_progress[reaction.message.guild.id]['participants'].remove(user)
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
            quiz_progress[message.guild.id]['message_id'] = message.id
            await message.add_reaction('🇾')
            await sleep(15)
            await message.delete()
            await quiz_refresh(message.guild.id)            
        if message.content.startswith("**Quiz ID:**"):
            guild_id = int(message.content.split('\n')[0].split()[2])
            print(guild_id)
            for i in loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]['options']: await message.add_reaction(i)

@quizbot.command(name = 'exit', aliases = ['kill', 'off', 'disconnect'])
async def exit(ctx):
    '''To turn off bot. Mainly for dev purposes. Won't be present in final one.'''
    print(f"Exit time: {datetime.now()}")
    await quizbot.close()


@quizbot.command(name = 'start_quiz', aliases = ['start', 'begin', 'begin_quiz'])
async def start_quiz(ctx, quiz_id: int):
    '''Starts the quiz. Afterwards, another async function will be used to run the quiz'''
    try: open(f'quizzes/{quiz_id}.json', encoding = 'utf-16').close()
    except:
        await ctx.send("Quiz ID does not exist. Please check the quiz ID or contact Goos.")
        return None
    if quiz_progress[ctx.message.guild.id]: 
        await ctx.send("A quiz is already registered in this server. ")
        return None
    quiz_progress[ctx.message.guild.id] = {'quiz_id': quiz_id , 'participants' : [] , 'status' : 0, 'channel' : ctx.channel}
    await ctx.send(f"**Starting Quiz ID:** {quiz_id}. React with 🇾 to participate within 15 seconds.")

quizbot.run(token)
#Honk