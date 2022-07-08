# Quiz Bot 

__My first GitHub project:__ A Quiz Bot for MASK using discord.py.

##
### :star: Announcement: :star:
I will be working on making the bot to conduct quizzes using image questions. This will hopefully be done by EoD of Sunday (10 Juy 2022). 

*(moving on...)*
##


## Purpose:
The idea to make this bot came when we had our first MASK quiz. It is expected that none of us knew _that_ many animes and we were forced to rely on herd mentality. Because of this one reason, the purpose of the quiz was somewhat nullified. In order to make the responses anonymous, this bot will be using the DMs to send questions and receive responses rather than using a channel common to all participants.

## How will it work?:

The rough idea of how it works is as follows:
- Start a quiz with the command `start [quiz_id]`
- Check for users who are participating and storing that information
- Sending questions one-by-one to all members simultaneously with appropriate reaction emojis
- Collecting user responses for each question
- Compiling and calculating the result of the quiz
- Announcing in the channel

### A bit more in depth 

First, the command `start` checks for the respective quiz's presence and waits for the participants to accept the quiz. The acceptance will be by an emoji reaction to the message. If one chooses to remove their reaction, they will not be participating. After 15 seconds, the message will be deleted and the participants will be sent a DM saying that they have been registered to the quiz, and an announcement in the channel where the command will be sent with the list of participants. 

After this, the questions will be sent to the participants simultaneously. The questions are sent one-by-one with a gap of 17.5 seconds in between consecutive questions. Each question message will be having the reactions attached with it. The participant may choose to either react or skip. If the participant reacts another emoji after reacting once, the new reaction will overwrite the old reaction, forcing the participant to remove and add the original reaction to select the former option as their final choice.

After the 17.5 second gap, the question message will be deleted and the next message sent by the bot will have the next question with the same process as mentioned above. Once all questions are done, the final result will be calculated and announced in the channel where the command was originally sent. 


## Commands in the Quiz-Bot:

```
[start | begin | start_quiz | begin_quiz] {quiz_id}: To start a quiz.
[list | available | available_quizzes]: Lists all available quizzes as of the moment.
[info | describe] {quiz_id}: To give the title/description of a quiz.
[terminate]: To stop a quiz midway if it is started by mistake.
```

### New commands which are expected to be added:

```
[skip]: To skip a quiz if the participant chooses not to continue.
```

## Storing Data:

The quizzes are stored in JSON files with names _quiz_id_.json in the following format: 

```js
{
	"quiz_length" : number_of_questions,
	"quiz":
	[
		{
			"sauce" : "Name of the Anime/Manga" , 
			"text" : "The text of the question",
			"options" :
			{
				"🇦" : "Option A",
				"🇧" : "Option B",                
				"🇨" : "Option C",
				"🇩" : "Option D"
			}, 
			"correct_option" : "key of correct option"
		},
		...
	]
}
```

The descriptions are stored in another JSON file, i.e., `descriptions.json` in the following format:

```js
{
	"quizzes" :
	[
		{
			"quiz_id" : quiz_id,
			"quiz_name" : "Name of the quiz",
			"quiz_length" : number_of_questions,
			"quiz_description" : "A string with a brief description of the quiz"
		},
		...
	]
}
```

##

Using Python's built-in JSON package, the bot extracts the description file, and the quizzes whenever they are needed. The progress of all quizzes currently active are stored in a dictionary `quiz_progress` which has the information on all currently running quizzes. The values are stored in this format.

```python
quiz_progress = {
	server_1_id : {'quiz_id' : quiz_id, 'participants' : [list of participants], 'status' : current_question_status, 'channel' : channel_object},
	server_2_id : {...},
	...
}
```

- `quiz_id` is an integer as mentioned in earlier instances.
- The list of `participants` gets updated as they react to the message relating to the quiz participation.
- `status` represents the current question number. status = 0 implies waiting for participants to sign-up
- `channel` represents the channel where the start command was called. All messages, from the participant list to the results will be sent to that channel

Quizzes are loaded and stored in a separate dictionary `loaded_quizzes`. The values are stored in this format

```python
loaded_quizzes = {
	server_1_id : json file loaded as dict,
	...
}
```

The responses by the participants are also stored in a dictionary `responses`. The values are stored in this format

```python
responses = {
	user_1_id : {'guild_id' :guild_where_quiz_going_on, 'response' : [list of responses]},
	...
}
```


## 

More details will be updated soon ig. 
Until then, this is your goose, signing off. 

Honk
