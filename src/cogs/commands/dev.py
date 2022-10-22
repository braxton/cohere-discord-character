import io
import os
import logging
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Text

import discord
from discord import app_commands
from discord import TextChannel
from discord.ext import commands

from src.bot import Character_Bot

log = logging.getLogger(__name__)


class DeveloperCommands(commands.Cog):

    def __init__(self, bot: Character_Bot) -> None:
        self.bot = bot
        self._last_result = None

    def _cleanup_code(self, content: str) -> str:
        """
        Automatically removes code blocks from the code.
        """
        # remove ```py\n```
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        # remove `foo`
        return content.strip("` \n")

    @app_commands.command(name="eval", description="Evaluates Python code from previous message")
    @app_commands.guilds(discord.Object(os.environ.get("DISCORD_GUILD_ID", "DISCORD_GUILD_ID_MISSING")))
    @app_commands.guild_only()
    async def eval(self, ctx: discord.Interaction):
        """
        Evaluates input as Python code.
        """

        await ctx.response.defer(thinking=True, ephemeral=True)

        if not await self.bot.is_owner(ctx.user):
            return await ctx.followup.send("ERR: You are not the owner of this bot", ephemeral=True)

        if not ctx.channel or not isinstance(ctx.channel, TextChannel):
            return await ctx.followup.send("ERR: Unable to define channel", ephemeral=True)

        # Required environment variables.
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.user,
            "guild": ctx.guild,
            "ctx": ctx,
            "_": self._last_result,
        }

        msgs = [
            x async for x in ctx.channel.history(
                limit=10) if x.author.id == ctx.user.id and x.content.startswith("```") and x.content.endswith("```")
        ]
        if len(msgs) == 0:
            return await ctx.followup.send("Unable to find code to execute", ephemeral=True)

        msg = msgs[0]

        body = msg.content
        # Creating embed.
        embed = discord.Embed(title="Evaluating.", color=0xB134EB)
        env.update(globals())

        # Calling cleanup command to remove the markdown traces.
        body = self._cleanup_code(body)
        embed.add_field(name="Input:", value=f"```py\n{body}\n```", inline=False)
        # Output stream.
        stdout = io.StringIO()

        # Exact code to be compiled.
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            # Attempting execution
            exec(to_compile, env)
        except Exception as e:
            # In case there's an error, add it to the embed, send and stop.
            errors = f"```py\n{e.__class__.__name__}: {e}\n```"
            embed.add_field(name="Errors:", value=errors, inline=False)
            await ctx.followup.send(embed=embed)
            return errors

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            # In case there's an error, add it to the embed, send and stop.
            value = stdout.getvalue()
            errors = f"```py\n{value}{traceback.format_exc()}\n```"
            embed.add_field(name="Errors:", value=errors, inline=False)
            await ctx.followup.send(embed=embed)

        else:
            value = stdout.getvalue()
            try:
                await msg.add_reaction("\u2705")
            except Exception:
                pass

            if ret is None:
                if value:
                    # Output.
                    output = f"```py\n{value}\n```"
                    embed.add_field(name="Output:", value=output, inline=False)
                    await ctx.followup.send(embed=embed)
                else:
                    # no output, so remove the "bot is thinking... message"
                    response = await ctx.followup.send("** **")
            else:
                # Maybe the case where there's no output?
                self._last_result = ret
                output = f"```py\n{value}{ret}\n```"
                embed.add_field(name="Output:", value=output, inline=False)
                await ctx.followup.send(embed=embed)


async def setup(bot: Character_Bot) -> None:
    await bot.add_cog(DeveloperCommands(bot))
    log.info("Commands loaded: dev")