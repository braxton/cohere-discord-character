import logging

import discord
from discord.ext import commands

from src.bot import Character_Bot
from src.utils import cohere

log = logging.getLogger(__name__)


class AutoresponderListeners(commands.Cog):

    def __init__(self, bot: Character_Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Scan incoming messages for mentions and processes the message as input to Cohere's model
        """
        if message.author.bot:
            return

        if self.bot.user.mention not in message.content: # type: ignore
            return


        history = []
        ctx = await self.bot.get_context(message)
        async with ctx.typing():
            async for msg in message.channel.history(limit=6):
                if msg.content:
                    history = [[msg.author.name, cohere.strip_mentions(msg.clean_content)]] + history
            await message.reply(cohere.generate_response(self.bot, history))


async def setup(bot: Character_Bot) -> None:
    await bot.add_cog(AutoresponderListeners(bot))
    log.info("Listeners Loaded: autoresponder")