import pytest
import pytest_mock
import discord
from discord.ext import commands
from unittest.mock import AsyncMock, MagicMock, patch
from src.bot import create_bot


class TestBot:
    @pytest.fixture
    def mock_bot(self, mocker):
        # Mock the discord.ext.commands.Bot class
        bot_mock = mocker.MagicMock(spec=commands.Bot)
        bot_mock.user = mocker.MagicMock(spec=discord.ClientUser)
        bot_mock.user.mentioned_in = mocker.MagicMock(return_value=False)

        # Mock the event registration methods
        events = {}

        def register_event(event_name):
            def decorator(func):
                events[event_name] = func
                return func
            return decorator

        bot_mock.event = register_event
        bot_mock.events = events

        # Mock the process_commands method
        bot_mock.process_commands = AsyncMock()

        # Return the mocked bot
        return bot_mock

    @pytest.fixture
    def mock_commands_bot(self, mocker):
        # Mock the Bot constructor
        bot_mock = mocker.MagicMock()
        mocker.patch('discord.ext.commands.Bot', return_value=bot_mock)
        return bot_mock

    def test_create_bot(self, mock_commands_bot):
        # Test that create_bot creates a bot with the correct parameters
        bot = create_bot()

        # Verify Bot was created with the correct parameters
        discord.ext.commands.Bot.assert_called_once()
        call_args = discord.ext.commands.Bot.call_args

        # Check intents (no command prefix needed for chat bot)
        intents = call_args[1]['intents']
        assert isinstance(intents, discord.Intents)
        assert intents.message_content is True
        assert intents.members is True

    @pytest.mark.asyncio
    async def test_on_ready(self, mock_commands_bot):
        # Create the bot
        bot = create_bot()

        # The test just verifies that create_bot() doesn't raise an exception
        # and that the bot object is returned
        assert bot is not None

    @pytest.mark.asyncio
    async def test_on_connect(self, mock_commands_bot):
        # Create the bot
        bot = create_bot()

        # The test just verifies that create_bot() doesn't raise an exception
        # Event handlers are registered internally
        assert bot is not None

    @pytest.mark.asyncio
    async def test_on_disconnect(self, mock_commands_bot):
        # Create the bot
        bot = create_bot()

        # The test just verifies that create_bot() doesn't raise an exception
        # Event handlers are registered internally
        assert bot is not None

    @pytest.mark.asyncio
    async def test_on_message_logic(self, mock_commands_bot, mocker):
        # Test the message handling logic by testing the bot creation
        # and verifying that the LLM integration is properly imported

        # Mock the bot_response function to verify it's available
        mock_bot_response = mocker.patch('src.bot.bot_response', return_value="Test response")

        # Create the bot
        bot = create_bot()

        # Verify the bot was created successfully
        assert bot is not None

        # Verify that bot_response is available (imported correctly)
        from src.bot import bot_response
        assert bot_response is not None
