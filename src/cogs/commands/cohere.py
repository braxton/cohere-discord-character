import logging
import os
from io import BytesIO

import dataset
import discord
from discord import app_commands
from discord.ext import commands

import utils.database as database
from src.bot import Character_Bot
from src.utils import cohere

log = logging.getLogger(__name__)


class CharacterModal(discord.ui.Modal, title='Cohere Character Config'):
    char_name = discord.ui.TextInput(label="Name",
                                     style=discord.TextStyle.short,
                                     placeholder='Enter a name for your character...',
                                     required=True)

    char_desc = discord.ui.TextInput(label='Description',
                                     style=discord.TextStyle.paragraph,
                                     placeholder='Enter a description for your character...',
                                     required=True)

    async def on_submit(self, ctx: discord.Interaction):
        db = database.Database().get()
        settings_db: dataset.Table | None = db["settings"]
        assert settings_db is not None

        settings_db.update(dict(guild_id=ctx.guild_id, char_name=self.char_name, char_desc=self.char_desc),
                           ["guild_id"])
        db.commit()
        db.close()

        if ctx.guild is not None:
            await ctx.guild.me.edit(
                nick=str(self.char_name) if self.char_name != "" else None
            )

        await ctx.response.send_message(
            f'NPC status: Character config updated!\n\nName: `{self.char_name}`\nDescription: `{self.char_desc}`')

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        log.error(f'Error in modal: {error.__traceback__}')

class CohereCommands(commands.Cog):

    def __init__(self, bot: Character_Bot) -> None:
        self.bot = bot

    @app_commands.checks.has_permissions(administrator=True)
    class CohereGroup(app_commands.Group):
        pass

    cohere_group = CohereGroup(name="server", description="Server management commands")

    @cohere_group.command(name="character", description="Configures server Cohere character")
    async def character(self, ctx: discord.Interaction):
        await ctx.response.send_modal(CharacterModal())

    @cohere_group.command(name="pfp",
                          description="Generate a profile picture for your bot based it's name and description.")
    async def profile_picture(self, ctx: discord.Interaction):
        await ctx.response.defer()
        db = database.Database().get()
        settings_db: dataset.Table | None = db["settings"]
        assert settings_db is not None

        guild_settings = settings_db.find_one(guild_id=ctx.guild_id)
        db.close()

        char_name = None
        char_desc = None
        if guild_settings is not None:
            char_name = guild_settings["char_name"]
            char_desc = guild_settings["char_desc"]

        img = cohere.profile_picture(self.bot, char_name, char_desc)

        with BytesIO() as image_binary:
            img.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.followup.send('', file=discord.File(fp=image_binary, filename='profile.png'))


async def setup(bot: Character_Bot) -> None:
    await bot.add_cog(CohereCommands(bot))
    log.info("Commands loaded: cohere")