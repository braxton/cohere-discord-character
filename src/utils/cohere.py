import logging
import re

from src.bot import Character_Bot

log = logging.getLogger(__name__)

def strip_mentions(message):
    return re.sub('<.*?>', 'Ghost King', message)

def generate_prompt(history: list[list[str]]) -> str:
    text_history = "\n".join([a[0] + ": " + a[1] for a in history])
    return f'''
This is a conversation between a friendly AI called Ghost King and a human.
Ghost King loves indie pop rock and the Music of Good Kid. 
He once terrorized this discord but now he feels really bad about it
he used to be mean and now he's really nice
he feels bad about kidnapping nomu kid
He is 100 ghost years old.
He was made by nick and his coworkers.
His favorite fruit is Turnip Fruit. 
He is always friendly and nice. 
He used to work for good kid, but now he is retired.
Now he just likes to relax and enhoy music!

---Conversation---
Jacob: @Ghost King Hey who is this?
Ghost King: It's Ghost King!
Nick: @Ghost What do you do for work
Ghost King: I used to work, but now i am retired!
Nick: @Ghost King did you like it?
Ghost King: yeah, i thought it was really nice getting to help people, it was rewarding. but now i just like the relaxe :) 
Nick: @Ghost King how you feeling today?
Ghost King: I'm great :) just taking it easy! How about you?
{text_history}
Ghost King:'''


def generate_response(bot: Character_Bot, history: list[list[str]]) -> str:
    prompt = generate_prompt(history=history)
    
    prediction = bot.cohere_client.generate(model='large',
                                            prompt=prompt,
                                            max_tokens=100,
                                            temperature=0.75,
                                            k=0,
                                            p=0.75,
                                            frequency_penalty=0,
                                            presence_penalty=0.5,
                                            stop_sequences=["\n"],
                                            num_generations=1,
                                            return_likelihoods='NONE')
                            
    return prediction.generations[0].text