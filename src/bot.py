import asyncio
import glob
import logging
import os

import cohere
import dataset
import discord
from discord.ext import commands

import __init__
import utils.database as database


class Character_Bot(commands.Bot):

    def __init__(self, cohere_api_key: str, *args, **kwargs):
        if cohere_api_key == "":
            raise Exception("Missing COHERE_API_KEY env var")

        self.cohere_client = cohere.Client(cohere_api_key)
        super(self.__class__, self).__init__(*args, **kwargs)


bot = Character_Bot(
    #activity=discord.Activity(type=discord.ActivityType.listening, name="to your messages"),
    case_insensitive=True,
    cohere_api_key=os.environ.get("COHERE_API_KEY", ""),
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
    log.info(f"Logged in as: {str(bot.user)}")

    if os.environ.get("DISCORD_GUILD_ID") == None:
        raise Exception("Missing DISCORD_GUILD_ID env var")

    # Sync dev guild commands
    await bot.tree.sync(guild=discord.Object(os.environ.get("DISCORD_GUILD_ID", "")))
    # Sync global commands
    await bot.tree.sync(guild=None)


@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
    db = database.Database().get()
    settings_db: dataset.Table | None = db["settings"]
    assert settings_db is not None

    pk = settings_db.insert(dict(guild_id=guild.id))

    db.commit()
    db.close()

    log.info(f"Guild Joined: {pk} - {guild.id}")


@bot.event
async def on_guild_remove(guild: discord.Guild) -> None:
    db = database.Database().get()
    settings_db: dataset.Table | None = db["settings"]
    assert settings_db is not None

    settings_db.delete(guild_id=guild.id)
    db.commit()
    db.close()

    log.info(f"Guild Left: {guild.id}")


async def main():
    cogs_path = os.path.join("cogs", "**", "[!^_]*.py")

    for cog in glob.iglob(cogs_path, root_dir="src", recursive=True):
        # Convert Unix/Windows paths to Python module paths
        cog_name_fmted = cog \
            .replace("/", ".") \
            .replace("\\", ".") \
            .replace(".py", "")

        await bot.load_extension(cog_name_fmted)

    if os.environ.get("DISCORD_BOT_TOKEN") == None:
        raise Exception("Missing DISCORD_BOT_TOKEN env var")

    await bot.start(os.environ.get("DISCORD_BOT_TOKEN", ""))


if __name__ == "__main__":
    database.Database().setup()
    asyncio.run(main())