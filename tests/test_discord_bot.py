import pytest
import pytest_mock
import discord
from discord.ext import commands
from unittest.mock import AsyncMock, MagicMock, patch
from src.bot import create_bot


class TestBot:
    def test_create_bot_intents(self):
        """Test that create_bot creates a bot with the correct intents."""
        with patch('discord.ext.commands.Bot') as mock_bot_class:
            mock_bot_instance = MagicMock()
            mock_bot_class.return_value = mock_bot_instance

            bot = create_bot()

            # Verify Bot was called once
            mock_bot_class.assert_called_once()
            call_args = mock_bot_class.call_args

            # Check intents
            intents = call_args[1]['intents']
            assert isinstance(intents, discord.Intents)
            assert intents.message_content is True
            assert intents.members is True

            # Verify the bot instance is returned
            assert bot == mock_bot_instance

    @pytest.mark.asyncio
    async def test_on_message_bot_ignores_own_messages(self, mocker):
        """Test that the bot ignores its own messages."""
        with patch('discord.ext.commands.Bot') as mock_bot_class:
            mock_bot_instance = MagicMock()
            mock_bot_class.return_value = mock_bot_instance

            # Capture the on_message handler
            on_message_handler = None
            def capture_event(func):
                nonlocal on_message_handler
                if func.__name__ == 'on_message':
                    on_message_handler = func
                return func

            mock_bot_instance.event = capture_event

            # Create the bot to register event handlers
            bot = create_bot()

            # Create a mock message from the bot itself
            mock_message = MagicMock()
            mock_message.author = mock_bot_instance.user

            # Call the on_message handler
            result = await on_message_handler(mock_message)

            # Verify the function returns early (None) for bot's own messages
            assert result is None

    @pytest.mark.asyncio
    async def test_on_message_responds_to_mentions(self, mocker):
        """Test that the bot responds when mentioned."""
        # Mock the bot_response function
        mock_bot_response = mocker.patch('src.bot.bot_response', return_value="Test response")

        with patch('discord.ext.commands.Bot') as mock_bot_class:
            mock_bot_instance = MagicMock()
            mock_bot_class.return_value = mock_bot_instance

            # Capture the on_message handler
            on_message_handler = None
            def capture_event(func):
                nonlocal on_message_handler
                if func.__name__ == 'on_message':
                    on_message_handler = func
                return func

            mock_bot_instance.event = capture_event

            # Create the bot to register event handlers
            bot = create_bot()

            # Create a mock message that mentions the bot
            mock_message = MagicMock()
            mock_message.author = MagicMock()  # Different from bot.user
            mock_message.content = "Hello @bot, how are you?"
            mock_message.channel.send = AsyncMock()

            # Mock the mentioned_in method to return True
            mock_bot_instance.user.mentioned_in.return_value = True

            # Call the on_message handler
            await on_message_handler(mock_message)

            # Verify bot_response was called with the message content
            mock_bot_response.assert_called_once_with(prompt=mock_message.content)

            # Verify the response was sent to the channel
            mock_message.channel.send.assert_called_once_with("Test response")

    @pytest.mark.asyncio
    async def test_on_message_ignores_non_mentions(self, mocker):
        """Test that the bot ignores messages that don't mention it."""
        # Mock the bot_response function
        mock_bot_response = mocker.patch('src.bot.bot_response')

        with patch('discord.ext.commands.Bot') as mock_bot_class:
            mock_bot_instance = MagicMock()
            mock_bot_class.return_value = mock_bot_instance

            # Capture the on_message handler
            on_message_handler = None
            def capture_event(func):
                nonlocal on_message_handler
                if func.__name__ == 'on_message':
                    on_message_handler = func
                return func

            mock_bot_instance.event = capture_event

            # Create the bot to register event handlers
            bot = create_bot()

            # Create a mock message that doesn't mention the bot
            mock_message = MagicMock()
            mock_message.author = MagicMock()  # Different from bot.user
            mock_message.content = "Hello everyone!"
            mock_message.channel.send = AsyncMock()

            # Mock the mentioned_in method to return False
            mock_bot_instance.user.mentioned_in.return_value = False

            # Call the on_message handler
            await on_message_handler(mock_message)

            # Verify bot_response was NOT called
            mock_bot_response.assert_not_called()

            # Verify no message was sent to the channel
            mock_message.channel.send.assert_not_called()

    def test_event_handlers_registered(self):
        """Test that all expected event handlers are registered."""
        with patch('discord.ext.commands.Bot') as mock_bot_class:
            mock_bot_instance = MagicMock()
            mock_bot_class.return_value = mock_bot_instance

            # Track registered events
            registered_events = []
            def track_event(func):
                registered_events.append(func.__name__)
                return func

            mock_bot_instance.event = track_event

            # Create the bot to register event handlers
            bot = create_bot()

            # Verify all expected event handlers are registered
            expected_events = ['on_ready', 'on_connect', 'on_disconnect', 'on_message']
            for event in expected_events:
                assert event in registered_events, f"Event handler {event} not registered"
