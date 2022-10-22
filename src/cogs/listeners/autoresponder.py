import logging
import dataset

import discord
from discord.ext import commands

from src.bot import Character_Bot
from src.utils import cohere, database

log = logging.getLogger(__name__)


class AutoresponderListeners(commands.Cog):

    def __init__(self, bot: Character_Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Scan incoming messages for mentions and processes the message as input to Cohere's model
        """
        if message.author.bot or not message.guild:
            return

        if self.bot.user.mention not in message.content:  # type: ignore
            return

        db = database.Database().get()
        settings_db: dataset.Table | None = db["settings"]
        assert settings_db is not None

        guild_settings = settings_db.find_one(guild_id=message.guild.id)
        db.close()
        log.info(guild_settings)

        char_name = "NPC"
        char_desc = ''
        if guild_settings is not None:
            char_name = guild_settings["char_name"]
            char_desc = guild_settings["char_desc"]

        history = []
        ctx = await self.bot.get_context(message)
        async with ctx.typing():
            async for msg in message.channel.history(limit=6):
                if msg.content:
                    history = [[msg.author.name, cohere.strip_mentions(msg.clean_content, char_name)]] + history

            log.info(f"replying")
            response = cohere.generate_response(self.bot, history, char_name, char_desc)
            await message.reply(response)


async def setup(bot: Character_Bot) -> None:
    await bot.add_cog(AutoresponderListeners(bot))
    log.info("Listeners Loaded: autoresponder")