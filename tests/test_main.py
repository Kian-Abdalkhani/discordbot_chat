import pytest
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from src.main import main, async_main


class TestMain:
    @pytest.mark.asyncio
    async def test_async_main(self, mocker):
        """Test the async_main function."""
        # Mock dependencies
        mock_load_dotenv = mocker.patch('src.main.load_dotenv')
        mock_setup_logging = mocker.patch('src.main.setup_logging')
        mock_create_bot = mocker.patch('src.main.create_bot')
        mock_bot = MagicMock()
        mock_create_bot.return_value = mock_bot
        
        # Call async_main
        result = await async_main()
        
        # Verify all functions were called
        mock_load_dotenv.assert_called_once()
        mock_setup_logging.assert_called_once()
        mock_create_bot.assert_called_once()
        
        # Verify the bot is returned
        assert result == mock_bot

    def test_main_with_valid_token(self, mocker):
        """Test main function with valid bot token."""
        # Mock environment variable
        mocker.patch.dict(os.environ, {'BOT_TOKEN': 'test_token_123'})
        
        # Mock dependencies
        mock_async_main = mocker.patch('src.main.async_main')
        mock_bot = MagicMock()
        mock_bot.run = MagicMock()
        mock_async_main.return_value = mock_bot
        
        # Mock asyncio.new_event_loop and run_until_complete
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = mock_bot
        mocker.patch('asyncio.new_event_loop', return_value=mock_loop)
        
        # Call main function
        main()
        
        # Verify bot.run was called with the token
        mock_bot.run.assert_called_once_with('test_token_123')

    def test_main_without_token_exits(self, mocker):
        """Test main function exits when no bot token is provided."""
        # Mock environment without BOT_TOKEN
        mocker.patch.dict(os.environ, {}, clear=True)
        
        # Mock dependencies
        mock_async_main = mocker.patch('src.main.async_main')
        mock_bot = MagicMock()
        mock_async_main.return_value = mock_bot
        
        # Mock asyncio.new_event_loop and run_until_complete
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = mock_bot
        mocker.patch('asyncio.new_event_loop', return_value=mock_loop)
        
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch('sys.exit')
        
        # Mock logging.error
        mock_logging_error = mocker.patch('logging.error')
        
        # Call main function
        main()
        
        # Verify error was logged and sys.exit was called
        mock_logging_error.assert_called_once_with("No bot token found in environment variables")
        mock_exit.assert_called_once_with(1)

    def test_main_empty_token_exits(self, mocker):
        """Test main function exits when bot token is empty."""
        # Mock environment with empty BOT_TOKEN
        mocker.patch.dict(os.environ, {'BOT_TOKEN': ''})
        
        # Mock dependencies
        mock_async_main = mocker.patch('src.main.async_main')
        mock_bot = MagicMock()
        mock_async_main.return_value = mock_bot
        
        # Mock asyncio.new_event_loop and run_until_complete
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = mock_bot
        mocker.patch('asyncio.new_event_loop', return_value=mock_loop)
        
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch('sys.exit')
        
        # Mock logging.error
        mock_logging_error = mocker.patch('logging.error')
        
        # Call main function
        main()
        
        # Verify error was logged and sys.exit was called
        mock_logging_error.assert_called_once_with("No bot token found in environment variables")
        mock_exit.assert_called_once_with(1)

    def test_main_integration_flow(self, mocker):
        """Test the complete integration flow of main function."""
        # Mock environment variable
        mocker.patch.dict(os.environ, {'BOT_TOKEN': 'integration_test_token'})
        
        # Mock all the imported functions
        mock_load_dotenv = mocker.patch('src.main.load_dotenv')
        mock_setup_logging = mocker.patch('src.main.setup_logging')
        mock_create_bot = mocker.patch('src.main.create_bot')
        
        # Create a mock bot
        mock_bot = MagicMock()
        mock_bot.run = MagicMock()
        mock_create_bot.return_value = mock_bot
        
        # Mock asyncio components
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = mock_bot
        mocker.patch('asyncio.new_event_loop', return_value=mock_loop)
        
        # Call main function
        main()
        
        # Verify the complete flow
        mock_loop.run_until_complete.assert_called_once()
        mock_bot.run.assert_called_once_with('integration_test_token')