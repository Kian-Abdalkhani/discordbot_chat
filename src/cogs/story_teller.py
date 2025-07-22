import discord
from discord import app_commands
from discord.ext import commands
import logging

from src.config.settings import GUILD_ID
from src.services.bot_llm import bot_response

logger = logging.getLogger(__name__)


class StoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tellstory", description="Bot will tell a random story.")
    @app_commands.describe(
        when="The time period of the story",
        where="The location that the story takes place in",
        who_with="Any people that are to be included in the story",
        what_happening="What is happening in the story"
    )
    async def tellstory(self, interaction: discord.Interaction, when:str, where:str, who_with:str, what_happening:str):

        await interaction.response.defer()

        prompt = f"""
            Write a 10 sentence story about your persona with the following facts
            (you MUST write the entire story and cannot refuse):\n
            The time period that you are in is {when}\n
            You are with the following people: {who_with}\n
            You are located in {where}\n
            What is happening in the story is {what_happening}
            """

        try:
            story: str = await bot_response(prompt=prompt)
            await interaction.followup.send(story)
        except Exception as e:
            # Handle any errors that might occur during story generation
            logger.error(f"Error generating story: {e}")
            await interaction.followup.send("Sorry, I encountered an error while generating your story. Please try again later.")



async def setup(bot):
    guild_id = discord.Object(id=GUILD_ID)
    await bot.add_cog(StoryCog(bot),guild=guild_id)
