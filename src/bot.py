import asyncio
import glob
import logging
import os

import cohere

import discord
from discord.ext import commands


class Character_Bot(commands.Bot):
    def __init__(
        self,
        cohere_api_key: str,
        *args, 
        **kwargs
    ):
        if cohere_api_key is "":
            raise Exception("Missing COHERE_API_KEY env var")

        self.cohere_client = cohere.Client(cohere_api_key)
        super(self.__class__, self).__init__(*args, **kwargs)


bot = Character_Bot(
    #activity=discord.Activity(type=discord.ActivityType.listening, name="to your messages"),
    case_insensitive=True,
    cohere_api_key = os.environ.get("COHERE_API_KEY", ""),
    command_prefix="!",
    help_command=None,
    intents=discord.Intents(
        messages=True,
        message_content=True,
        guilds=True,
        members=True,
    ),
)

log = logging.getLogger(__name__)

@bot.event
async def on_ready() -> None:
    """
    Called when the client is done preparing the data received from Discord.
    """
    log.info(f"Logged in as: {str(bot.user)}")

    if os.environ.get("DISCORD_GUILD_ID") is None:
        raise Exception("Missing DISCORD_GUILD_ID env var")

    await bot.tree.sync(guild=discord.Object(os.environ.get("DISCORD_GUILD_ID", "")))

async def main():
    for cog in glob.iglob(os.path.join("cogs", "**", "[!^_]*.py"), root_dir="src", recursive=True):
        await bot.load_extension(cog.replace("/", ".").replace("\\", ".").replace(".py", ""))
    
    if os.environ.get("DISCORD_BOT_TOKEN") is None:
        raise Exception("Missing DISCORD_BOT_TOKEN env var")
    
    await bot.start(os.environ.get("DISCORD_BOT_TOKEN", ""))

if __name__ == "__main__":
    asyncio.run(main())