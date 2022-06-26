# Quiz Bot 

__My first GitHub project:__ A Quiz Bot for MASK using discord.py.

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
```

### New commands which are expected to be added:

```
[info | describe] {quiz_id}: To give the title/description of a quiz.
[terminate]: To stop a quiz midway if it is started by mistake.
[skip]: To skip a quiz if the participant chooses not to continue.
```

## 

More details will be updated soon ig. 
Until then, this is your goose, signing off. 

Honk
