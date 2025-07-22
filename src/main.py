import os
import logging
import sys

from dotenv import load_dotenv

import discord
from discord.ext import commands

from src.utils.logging import setup_logging
from src.config.settings import GUILD_ID
from src.services.bot_llm import bot_response

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

class MyClient(commands.Bot):

    def __init__(self) -> None:
        # set the bot intents
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)

        self.guild = discord.Object(id=GUILD_ID)

    async def on_ready(self):
        logger.info(f"{self.user} ready for commands")

        extensions = [
            'src.cogs.story_teller'
        ]

        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")

        try:
            synced = await self.tree.sync(guild=self.guild)
            logger.info(f"Synced {len(synced)} commands")
        except Exception as e:
            logger.error(f"Error syncing commands: {e}")

    async def on_connect(self):
        logger.info(f"{self.user} connected to discord successfully")

    async def on_disconnect(self):
        logger.info(f"{self.user} disconnected from discord")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if self.user.mentioned_in(message):
            logger.info(f"{message.author} mentioned bot in {message.channel}")
            try:
                response = await bot_response(prompt=message.content)
                await message.channel.send(response)
                logger.debug(f"Successfully responded to mention from {message.author}")
            except Exception as e:
                logger.error(f"Error responding to mention from {message.author}: {e}")
                await message.channel.send("Sorry, I encountered an error while processing your message.")



def main():
    # pass bot token to Client
    bot_token = os.getenv("TEST_TOKEN")
    if not bot_token:
        logging.error("No bot token found in environment variables")
        sys.exit(1)
    client = MyClient()
    client.run(bot_token)

if __name__ == "__main__":
    main()
