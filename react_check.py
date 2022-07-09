import discord, json
from asyncio import sleep
from datetime import datetime
from discord.ext import commands
from os import chdir, listdir

chdir('\\'.join(__file__.split('\\')[:-1]))     #Changing path to keep files in same folder
quizbot = commands.Bot(command_prefix = '0>', intents = discord.Intents.all(), help_command = None)
quiz_progress = {}          #For storing the progress of the quiz in a global scale
loaded_quizzes = {}         #To store the quizzes loaded from the JSON files
responses = {}              #To store the responses of the participants for the quizzes
moderation_roles = {}       #Need to be added to prevent misuse of some commands.

#Note: Save the bot token and the bot owner ID outside the folder having the bot code in token.txt and owner.txt
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
	#Loads Quiz from JSON file into storage
	with open(f'quizzes/{quiz_progress[guild_id]["quiz_id"]}.json', encoding = 'utf-16') as file:
		loaded_quizzes[guild_id] = json.load(file)
	#Checks if no participants are there
	if len(quiz_progress[guild_id]['participants'])==0:
		await quiz_progress[guild_id]['channel'].send("Uh oh. Nobody's participating. Try again later")
		quiz_progress.pop(guild_id)
		return None
	#Registers participants for the quiz and sends them a message
	for user in quiz_progress[guild_id]['participants']:
		print(user)
		if user in responses:
			await user.send(f"You are already registered in the quiz in server **{quizbot.get_guild(responses[user]['guild_id'])}**")
			continue
		responses[user] = {'guild_id' : guild_id, 'response' : [None for i in range(loaded_quizzes[guild_id]['quiz_length'])] }
		await user.send(f"You have been registered for **Quiz {quiz_progress[guild_id]['quiz_id']}** in server **{quizbot.get_guild(guild_id)}**")
	#Sends a message to the channel where the quiz was started.
	await quiz_progress[guild_id]['channel'].send("**Participants of the quiz:\n**" + '\n'.join([f'<@{user.id}>' for user in quiz_progress[guild_id]['participants']])+"\nQuiz will start in 5 seconds.")
	await sleep(5)
	#Sends questions one by one to each participant.
	quiz_progress[guild_id]['status'] = 1
	while quiz_progress[guild_id]['status'] <= loaded_quizzes[guild_id]['quiz_length']:
		#Checking for text question or pictorial question
		if 'text' in loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]:
			message_string = format_question(guild_id, loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1])
			img = None
		else:
			message_string = f"**Quiz ID:** {guild_id} | {quiz_progress[guild_id]['quiz_id']}"
			with open(loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]['image'], 'rb') as f:
				img = discord.File(f)
		for user in quiz_progress[guild_id]['participants']:
			await user.send(message_string, file=img)
		#Sleep for 17.5 seconds before sending next question. The reaction calculation will be done by on_reaction_add/remove
		await sleep(17.5)
		quiz_progress[guild_id]['status'] += 1
	else:
		#Calculates the result from the bot's response.
		results = []
		for user in quiz_progress[guild_id]['participants']:
			print(f"Responses of [{user}]: {responses[user]['response']}")
			results.append( {'user': user, 'marks': calculate_result(loaded_quizzes[guild_id]['quiz'], responses[user]['response'] ) })
			responses.pop(user)
		#Sort results according to points and sending it.
		results = sorted(results, key = lambda x: x['marks'], reverse = True)
		await quiz_progress[guild_id]['channel'].send(format_results(results))
		#Deleting the records.
		for i in list(quiz_progress[guild_id].keys()): del quiz_progress[guild_id][i] 
		quiz_progress[guild_id] = None
		del loaded_quizzes[(guild_id)]

#Quizbot events: General events like message add, reaction add/remove, message sent, etc.

@quizbot.event
async def on_ready():
	'''Filler command to tell me that the bot is up.''' 
	print(f"Wake up time: {datetime.now()}")
	for guild in quizbot.guilds: 
		print(f"Up and running in server [{guild}]")
		quiz_progress[guild.id] = None

@quizbot.event
async def on_reaction_add(reaction, user):
	'''On reaction add event. Here, it is mainly used to register options, partiipation vote, etc.'''
	#Note: The bot doesn't care if you react anything to other messages. Also, it doesn't care about its first reactions.
	if reaction.message.author == quizbot.user and user != quizbot.user:
		#Message in DMs. Used for checking reactions to quiz messages.
		if reaction.message.guild == None:
			#Checks if the message is a quiz message and the emoji reacted is an option.
			guild_id = responses[user]['guild_id']
			if reaction.message.content.startswith("**Quiz ID:**") and reaction.emoji in loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]['options']:
				#Note: Old response will be overwritten. And since the bot can't remove reactions in DMs, you'll have to DIY.
				responses[user]['response'][quiz_progress[guild_id]['status']-1] = reaction.emoji
				#Log statement just for reference.
				print(f"{user} reacted {reaction.emoji} to question {quiz_progress[guild_id]['status']}")
		else:
			#Checks if the message is a quiz register message
			if reaction.message.content.startswith("**Starting Quiz ID:**"):
				#Checks if the reaction is the emoji [Y] and is reacted before the quiz starts. (Originally not disappearing message, so extra check.)
				if reaction.emoji == '🇾' and quiz_progress[reaction.message.guild.id]['status']==0 and reaction.message.id == quiz_progress[reaction.message.guild.id]['message_id']:
					quiz_progress[reaction.message.guild.id]['participants'].append(user)
					print(f"Participant added: {user.name}")

@quizbot.event
async def on_reaction_remove(reaction, user):
	'''On reaction add event. Here, it is mainly used to register options, partiipation vote, etc. similar to its add counterpart.'''
	#I hope no comment is fine considering the details are more or less the same fro
	if reaction.message.author == quizbot.user and quizbot.user != user:
		if reaction.message.guild == None:
			guild_id = responses[user]['guild_id']
			if reaction.message.content.startswith("**Quiz ID:**") and user != quizbot.user and reaction.emoji == responses[user]['response'][quiz_progress[guild_id]['status']-1]:
				responses[user]['response'][quiz_progress[guild_id]['status']-1] = None
				print(f"{user} withdrew his reaction to question {quiz_progress[guild_id]['status']}")
		else:
			if reaction.message.content.startswith("**Starting Quiz ID:**"):
				if user != quizbot.user and reaction.emoji == '🇾' and quiz_progress[reaction.message.guild.id]['status']==0 and reaction.message.id == quiz_progress[reaction.message.guild.id]['message_id']:
					quiz_progress[reaction.message.guild.id]['participants'].remove(user)
					print(f"Participant removed: {user.name}")

@quizbot.event
async def on_message(message):
	'''The core of user interface of the bot. If this fails, it's as good as bot being dead. It. Has. Everything.'''
	#Bot command checks (Ignores all unnecessary messages.)
	if message.author != quizbot.user and message.content.startswith(quizbot.command_prefix):
		try: 
			await quizbot.process_commands(message)
		except discord.ext.commands.errors.CommandNotFound: await message.channel.send("Command does not exist. :-!")
	#QuizBot messages. Reaction addition, awaiting, deleting, you name it. It's all here.
	elif message.author == quizbot.user:
		#No need to explain. If it's a quiz registry message, add a reaction, wait a few seconds, delete the message and start it.
		if message.content.startswith("**Starting Quiz ID:**"):
			quiz_progress[message.guild.id]['message_id'] = message.id
			await message.add_reaction('🇾')
			await sleep(15)
			await message.delete()
			await quiz_refresh(message.guild.id)
		#If it's a quiz question, get the quiz, add the option reactions, wait a few seconds and delete.
		if message.content.startswith("**Quiz ID:**"):
			guild_id = int(message.content.split('\n')[0].split()[2])
			for i in loaded_quizzes[guild_id]['quiz'][quiz_progress[guild_id]['status']-1]['options']: await message.add_reaction(i)
			await sleep(15)
			await message.delete()
		#Generic delete message command to remove cluster of messages (especially annoying when the bot is being tested.)
		if message.content.startswith("You have been registered") or message.content.startswith("The quiz will be stopped"):
			await sleep(5)
			await message.delete()

#QuizBot Commands: Specific commands which can be called using the command prefix.

@quizbot.command(name = 'help')
async def help(ctx):
	'''Please don't booli me.'''
	await ctx.send("Hello. Goose is lazy so hasn't made a help command yet. Blame him for this :skull: \nMeanwhile, check the README link in the repository. At least he has done some stuff there (*\*sigh\**) \nClick here:https://github.com/Goose-Of-War/quiz-bot/blob/main/README.md")

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
	#Not in server, no quiz for you. Imagine farming experience using this mechanism once the quizzes are released lol.
	if ctx.guild == None:
		await ctx.send("This command is supported only in servers. Please don't use this command in DMs. ")
		return None
	#Testing if the file is present. If not, send a message saying no quiz of said name exists.
	try: open(f'quizzes/{quiz_id}.json', encoding = 'utf-16').close()
	except:
		await ctx.send("Quiz ID does not exist. Please check the quiz ID or contact Goos.")
		return None
	#Check if the server already has an ongoing quiz registered in it.
	if quiz_progress[ctx.message.guild.id]: 
		await ctx.send("A quiz is already registered in this server. ")
		return None
	#If no error comes, register the server in the dict and send a message. Rest will be done by the om_message event.
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
	#Note: Currently, any participant and the bot owner can stop any quizzes.
	if ctx.guild:
		if ctx.guild.id in quiz_progress and ctx.message.author in quiz_progress[ctx.guild.id]['participants']+[quizbot.get_user(owner)]: 
			await ctx.send("The quiz will be stopped in a few seconds. Please ignore the next quiz message, if any.")
			for i in list(quiz_progress[ctx.guild.id].keys()): del quiz_progress[ctx.guild.id][i] 
			quiz_progress[ctx.guild.id] = None
			loaded_quizzes.pop(ctx.guild.id)
			for user in responses:
				if responses[user]['guild_id'] == ctx.guild.id: responses.pop(user);
		else:
			await ctx.send("There are no quizzes registered in this server as of now.")
	else:
		if ctx.message.author in responses:
			guild_id = responses[ctx.message.author]['guild_id']
			await ctx.send("The quiz will be stopped in a few seconds. Please ignore the next quiz message, if any.")
			await quiz_progress[guild_id]['channel'].send(f"The quiz will be stopped in a few seconds. Please ignore the next quiz message, if any. (stopped by {ctx.message.author}")
			for i in list(quiz_progress[guild_id].keys()): del quiz_progress[guild_id][i] 
			quiz_progress[guild_id] = None
			loaded_quizzes.pop(guild_id)
			for user in responses:
				if responses[user]['guild_id'] == guild_id: responses.pop(user);
		else:
			await ctx.send("You are not registered in any quizzes.")

@quizbot.command(name = 'describe', aliases = ['desc', 'info', 'deets'])
async def quiz_info(ctx, quiz_id: int):
	'''Sends the quiz details to the user.'''
	for quiz in descriptions:
		if quiz['quiz_id'] == quiz_id:
			await ctx.send("\n".join([f"**{i.replace('_',' ').capitalize()}**: {quiz[i]}" for i in quiz]))

quizbot.run(token)
#Honk