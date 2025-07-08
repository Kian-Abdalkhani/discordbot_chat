import logging
import sys
import os
import asyncio

from dotenv import load_dotenv

from src.bot import create_bot
from src.utils.logging import setup_logging


async def async_main():

    load_dotenv()
    setup_logging()
    bot = create_bot()

    return bot

def main():
    loop = asyncio.new_event_loop()
    bot = loop.run_until_complete(async_main())

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logging.error("No bot token found in environment variables")
        sys.exit(1)
    bot.run(bot_token)

if __name__ == "__main__":
    main()
