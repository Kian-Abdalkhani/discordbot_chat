import pytest
from src.services.bot_llm import bot_response, OLLAMA_MODEL

# Tests blank prompts
@pytest.mark.asyncio
async def test_bot_response_blank():
    with pytest.raises(ValueError, match="Please enter a prompt."):
        await bot_response(prompt="")

# Tests if invalid user is input into bot_response
@pytest.mark.asyncio
async def test_bot_response_invalid_user():
    with pytest.raises(ValueError, match="larry is not a Invalid user, please use 'system' or 'user'"):
        await bot_response(user="larry", prompt="Tell me a joke")

# Tests if api is called with correct parameters
@pytest.mark.asyncio
async def test_bot_response_ollama_api_call(mocker):
    # Mock the environment variable
    mocker.patch.dict('os.environ', {'OLLAMA_API_URL': 'http://127.0.0.1:11434'})

    # Mock the AsyncClient class
    mock_client_instance = mocker.AsyncMock()
    mock_client = mocker.patch("src.services.bot_llm.AsyncClient", return_value=mock_client_instance)

    # Mock the chat method
    mock_client_instance.chat.return_value = {
        'message': {'content': 'Mocked response'}
    }

    # Call the function
    result = await bot_response(prompt="Why did the chicken cross the road?")

    # Verify the client was created with the correct host
    mock_client.assert_called_once_with(host="http://127.0.0.1:11434")

    # Verify chat was called with the correct parameters
    mock_client_instance.chat.assert_called_once_with(
        model=OLLAMA_MODEL,
        messages=[
            {
                'role': 'user',
                'content': 'Why did the chicken cross the road?',
            },
        ]
    )

    # Verify the result
    assert result == 'Mocked response'

# Tests if system role is properly passed
@pytest.mark.asyncio
async def test_bot_response_system_role(mocker):
    # Mock the AsyncClient class
    mock_client_instance = mocker.AsyncMock()
    mock_client = mocker.patch("src.services.bot_llm.AsyncClient", return_value=mock_client_instance)

    # Mock the chat method
    mock_client_instance.chat.return_value = {
        'message': {'content': 'System response'}
    }

    # Call the function with system role
    result = await bot_response(user="system", prompt="You are a helpful assistant")

    # Verify chat was called with the correct role
    mock_client_instance.chat.assert_called_once_with(
        model=OLLAMA_MODEL,
        messages=[
            {
                'role': 'system',
                'content': 'You are a helpful assistant',
            },
        ]
    )

    # Verify the result
    assert result == 'System response'

# Tests if connection error is properly handled
@pytest.mark.asyncio
async def test_bot_response_connection_error(mocker):
    # Mock the AsyncClient class
    mock_client_instance = mocker.AsyncMock()
    mock_client = mocker.patch("src.services.bot_llm.AsyncClient", return_value=mock_client_instance)

    # Mock the chat method to raise ConnectionError
    mock_client_instance.chat.side_effect = ConnectionError("Connection failed")

    # Verify that the function raises the expected error
    with pytest.raises(ConnectionError, match="Could not connect to Ollama, please ensure Ollama is running."):
        await bot_response(prompt="Are you on?")

# Tests if HTTP errors are properly propagated
@pytest.mark.asyncio
async def test_bot_response_http_error(mocker):
    # Mock the AsyncClient class
    mock_client_instance = mocker.AsyncMock()
    mock_client = mocker.patch("src.services.bot_llm.AsyncClient", return_value=mock_client_instance)

    # Import HTTPError for the test
    from httpx import HTTPError

    # Mock the chat method to raise HTTPError
    mock_client_instance.chat.side_effect = HTTPError("HTTP Error")

    # Verify that the function allows the HTTPError to propagate
    with pytest.raises(HTTPError):
        await bot_response(prompt="Generate an error")

# Tests if ollama api is able to connect (integration test)
@pytest.mark.asyncio
async def test_ollama_connection():
    try:
        await bot_response(prompt="Are you on?")
    except ConnectionError:
        pytest.skip("Ollama service is not running, skipping integration test")
    except Exception as e:
        assert False, f"Unexpected error: {e}"
    else:
        assert True
