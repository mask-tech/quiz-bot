import discord, json
from asyncio import sleep
from datetime import datetime
from discord.ext import commands
from os import chdir, listdir

chdir('\\'.join(__file__.split('\\')[:-1]))     #Changing path to keep files in same folder
quizbot = commands.Bot(command_prefix = '<>', intents = discord.Intents.all(), help_command = None)
quiz_progress = {}          #For storing the progress of the quiz in a global scale
loaded_quizzes = {}         #To store the quizzes loaded from the JSON files
responses = {}              #To store the responses of the participants for the quizzes
moderation_roles = {}       #Need to be added to prevent misuse of some commands.

with open('\\'.join(__file__.split('\\')[:-2])+'\\token.txt') as file: token = file.read()
with open('\\'.join(__file__.split('\\')[:-2])+'\\owner.txt') as file: owner = int(file.read())
with open('quizzes/descriptions.json') as file: descriptions = json.load(file)['quizzes']

def format_question(guild_id: int, question: dict):
    '''Makes a string based on the question dict for the DM message.'''
    return f"**Quiz ID:** {guild_id} | {quiz_progress[guild_id]['quiz_id']}\n__**Sauce:**__ {question['sauce']}\n__**Text:**__ {question['text']}\n"+'\n'.join([f"{i} {question['options'][i]}" for i in question['options']])

def calculate_result(quiz: list, response: list):
    '''Calculates the result based on the quiz and responses.'''
    return sum([1 for i in range(len(quiz)) if quiz[i]['correct_option'] == response[i] ])

def format_results(results: list):
    '''Makes a string based on the sorted results for the message.'''
    output = "__**Result:**__\n"
    i = 1
    for j in range(len(results)):
        if j:
            if results[j]['marks'] != results[j-1]['marks']: i = j+1
        output += f"**{i}:** <@{results[j]['user'].id}> ({results[j]['marks']} pts)\n" 
    return output

async def quiz_refresh(guild_id):
    '''Main quiz work is done here.'''
    with open(f'quizzes/{quiz_progress[guild_id]["quiz_id"]}.json', encoding = 'utf-16') as file:
        loaded_quizzes[guild_id] = json.load(file)
    if len(quiz_progress[guild_id]['participants'])==0:
        await quiz_progress[guild_id]['channel'].send("Uh oh. Nobody's participating. Try again later")
        return None
    for user in quiz_progress[guild_id]['participants']:
        print(user)
        if user in responses:
            await user.send(f"You are already registered in the quiz in server **{quizbot.get_guild(responses[user]['guild_id'])}**")
            continue
        responses[user] = {'guild_id' : guild_id, 'response' : [None for i in range(loaded_quizzes[guild_id]['quiz_length'])] }
        await user.send(f"You have been registered for **Quiz {quiz_progress[guild_id]['quiz_id']}** in server **{quizbot.get_guild(guild_id)}**")
    await quiz_progress[guild_id]['channel'].send("**Participants of the quiz:\n**" + '\n'.join([f'<@{user.id}>' for user in quiz_progress[guild_id]['participants']])+"\nQuiz will start in 5 seconds.")
    await sleep(5)
    quiz_progress[guild_id]['status'] = 1
    while quiz_progress[guild_id]['status'] <= loaded_quizzes[guild_id]['quiz_length']:
        message_string = format_question(guild_id, loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1])
        for user in quiz_progress[guild_id]['participants']:
            await user.send(message_string)
        await sleep(17.5    )
        quiz_progress[guild_id]['status'] += 1
    else:
        results = []
        for user in quiz_progress[guild_id]['participants']:
            print(f"Responses of [{user}]: {responses[user]['response']}")
            results.append( {'user': user, 'marks': calculate_result(loaded_quizzes[guild_id]['quiz'], responses[user]['response'] ) })
            responses.pop(user)
        results = sorted(results, key = lambda x: x['marks'], reverse = True)
        await quiz_progress[guild_id]['channel'].send(format_results(results))
        quiz_progress.pop(guild_id)
        loaded_quizzes.pop(guild_id)

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
    if reaction.message.author == quizbot.user and user != quizbot.user:
        if reaction.message.guild == None:
            guild_id = responses[user]['guild_id']
            if reaction.message.content.startswith("**Quiz ID:**") and user != quizbot.user and reaction.emoji in loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]['options']:
                responses[user]['response'][quiz_progress[guild_id]['status']-1] = reaction.emoji
                print(f"{user} reacted {reaction.emoji} to question {quiz_progress[guild_id]['status']}")
        else:
            if reaction.message.content.startswith("**Starting Quiz ID:**"):
                if user != quizbot.user and reaction.emoji == '🇾' and quiz_progress[reaction.message.guild.id]['status']==0 and reaction.message.id == quiz_progress[reaction.message.guild.id]['message_id']:
                    quiz_progress[reaction.message.guild.id]['participants'].append(user)
                    print(f"Participant added: {user.name}")

@quizbot.event
async def on_reaction_remove(reaction, user):
    if reaction.message.author == quizbot.user and quizbot.user != user:
        if reaction.message.guild == None:
            guild_id = responses[user]['guild_id']
            if reaction.message.content.startswith("**Quiz ID:**") and user != quizbot.user and reaction.emoji == responses[user]['response'][quiz_progress[guild_id]['status']-1]:
                responses[user]['response'][quiz_progress[guild_id]['status']-1] = None
            
        else:
            if reaction.message.content.startswith("**Starting Quiz ID:**"):
                if user != quizbot.user and reaction.emoji == '🇾' and quiz_progress[reaction.message.guild.id]['status']==0 and reaction.message.id == quiz_progress[reaction.message.guild.id]['message_id']:
                    quiz_progress[reaction.message.guild.id]['participants'].remove(user)
                    print(f"Participant removed: {user.name}")

@quizbot.event
async def on_message(message):
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
            for i in loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]['options']: await message.add_reaction(i)
            await sleep(15)
            await message.delete()
        if message.content.startswith("You have been registered") or message.content.startswith("The quiz will be stopped"):
            await sleep(5)
            await message.delete()

@quizbot.command(name = 'exit', aliases = ['kill', 'off', 'disconnect'])
async def exit(ctx):
    '''To turn off bot. Mainly for dev purposes. Won't be present in final one.'''
    if ctx.message.author.id != owner:
        await ctx.send("You don't have the rights to tell me to go kill myself. Sus.")
        print(f"{ctx.message.author} in {ctx.guild} asked me to go die. Boohoo.")
        return None
    print(f"Exit time: {datetime.now()}")
    await quizbot.close()

@quizbot.command(name = 'start_quiz', aliases = ['start', 'begin', 'begin_quiz'])
async def start_quiz(ctx, quiz_id: int):
    '''Starts the quiz. Afterwards, another async function will be used to run the quiz'''
    if ctx.guild == None:
        await ctx.send("This command is supported only in servers. Please don't use this command in DMs. ")
    try: open(f'quizzes/{quiz_id}.json', encoding = 'utf-16').close()
    except:
        await ctx.send("Quiz ID does not exist. Please check the quiz ID or contact Goos.")
        return None
    if quiz_progress[ctx.message.guild.id]: 
        await ctx.send("A quiz is already registered in this server. ")
        return None
    quiz_progress[ctx.message.guild.id] = {'quiz_id': quiz_id , 'participants' : [] , 'status' : 0, 'channel' : ctx.channel}
    await ctx.send(f"**Starting Quiz ID:** {quiz_id}. React with 🇾 to participate within 15 seconds.")

@quizbot.command(name = 'available_quizzes', aliases = ['available', 'list'])
async def available_quizzes(ctx):
    '''To check for all available quizzes as of now.'''
    await ctx.send("Available quiz codes:\n```\n"+"\n".join([f"{i['quiz_id']}: {i['quiz_name']}" for i in descriptions])+'\n```')

@quizbot.command(name = 'terminate_quiz', aliases = ['stop','stop_quiz', 'terminate'])
async def terminate_quiz(ctx):
    '''To terminate the currently running quiz.'''
    print(f"Terminate called by {ctx.message.author}")
    if ctx.guild:
        if ctx.guild.id in quiz_progress and ctx.message.author in quiz_progress[ctx.guild.id]['participants']+[quizbot.get_user(owner)]: 
            await ctx.send("The quiz will be stopped in a few seconds. Please ignore the next quiz message, if any.")
            quiz_progress.pop(ctx.guild.id)
            loaded_quizzes.pop(ctx.guild.id)
            for user in responses:
                if responses[user]['guild_id'] == ctx.guild.id: responses.pop(user);
        else:
            await ctx.send("There are no quizzes registered in this server as of now.")
    else:
        if ctx.message.author in responses:
            guild_id = responses[ctx.message.author]['guild_id']
            await ctx.send("The quiz will be stopped in a few seconds. Please ignore the next quiz message, if any.")
            await quiz_progress[guild_id]['channel']("The quiz will be stopped in a few seconds. Please ignore the next quiz message, if any.")
            quiz_progress.pop(guild_id)
            loaded_quizzes.pop(guild_id)
            for user in responses:
                if responses[user]['guild_id'] == guild_id: responses.pop(user);
        else:
            await ctx.send("You are not registered in any quizzes.")

@quizbot.command(name = 'describe', aliases = ['desc', 'info', 'deets'])
async def quiz_info(ctx, quiz_id: int):
    for quiz in descriptions:
        if quiz['quiz_id'] == quiz_id:
            await ctx.send("\n".join([f"**{i.replace('_',' ').capitalize()}**: {quiz[i]}" for i in quiz]))

quizbot.run(token)
#Honk