import discord
from discord.ext import commands
import cohere
import yaml
import re
from good_kid_songs import *  
import random



with open('config.yml') as file:
    config = yaml.load(file)
yaml.dump(config, open('config.yml', "w"))

client = commands.Bot(command_prefix=config['command-prefix'])

co = cohere.Client(config['cohere_api_key'])

MODEL = 'large-20220217'

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    for guild in client.guilds:
        print(f'{client.user} is connected to the following guild:\n' f'{guild.name}(id: {guild.id})')



def strip_mentions(message):
    return re.sub('<.*?>', 'Ghost King', message)


def respond(history):
    text_history = "\n".join([a[0] + ": " + a[1] for a in history])
    prompt = f'''
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
    print(prompt)
    stop_sequences = ["\n"]
    prediction = co.generate(model='large',
                             prompt=prompt,
                             max_tokens=100,
                             temperature=0.75,
                             k=0,
                             p=0.75,
                             frequency_penalty=0,
                             presence_penalty=0.5,
                             stop_sequences=stop_sequences,
                             num_generations=1,
                             return_likelihoods='NONE')
                            
    return prediction.generations[0].text


@client.command('write_good_kid_lyrics')
async def write_good_kid_lyrics(ctx, *, name: str = ''):
    prompt = ''
    for key in random.sample(list(songs.keys()), 5):
        prompt += f"---\n{key} Lyrics:\n{songs[key]}"
    prompt += f"---\n{name} Lyrics:\n"

    stop_sequences = ["---"]

    async with ctx.typing():
        prediction = co.generate(model='large',
                                prompt=prompt,
                                max_tokens=200,
                                temperature=0.75,
                                k=0,
                                p=0.75,
                                frequency_penalty=0,
                                presence_penalty=0.5,
                                stop_sequences=stop_sequences,
                                num_generations=1,
                                return_likelihoods='NONE')
        await ctx.message.channel.send(prediction.generations[0].text, reference=ctx.message)
        return 


@client.event
async def on_message(message):
    if message.content:
        if message.content[0] == config['command-prefix']:
            await client.process_commands(message)
            return

        if message.author == client.user:
            return

        if client.user.mention in message.content:
            history = []
            ctx = await client.get_context(message)
            async with ctx.typing():
                async for msg in message.channel.history(limit=6):
                    if msg.content:
                        history = [[msg.author.name, strip_mentions(msg.clean_content)]] + history
                await message.channel.send(respond(history), reference=message)


client.run(config['discord_api_key'])