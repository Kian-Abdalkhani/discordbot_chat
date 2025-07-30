from httpx import HTTPError, HTTPStatusError
from ollama import AsyncClient
from ollama import ChatResponse
import os
import asyncio
import logging
import time

#enter the model from ollama that you would like to use and connect to Ollama:
OLLAMA_MODEL: str="boug_bot:HC"

logger = logging.getLogger(__name__)

# Only create the client when needed, not at import time
def get_client():
    ollama_url = os.getenv("OLLAMA_API_URL")
    logger.debug(f"Creating Ollama client with URL: {ollama_url}")
    return AsyncClient(host=ollama_url)

async def bot_response(user: str = "user", prompt: str = "") -> str:
    if not prompt:
        raise ValueError("Please enter a prompt.")
    if user not in ["user", "system"]:
        raise ValueError(f"{user} is not a Invalid user, please use 'system' or 'user'")
    logger.info(f"LLM request initiated - User: {user}, Prompt length: {len(prompt)} characters")
    logger.debug(f"Full prompt content: {prompt[:200]}..." if len(prompt) > 200 else f"Full prompt content: {prompt}")
    
    start_time = time.time()
    
    try:
        logger.debug(f"Connecting to Ollama with model: {OLLAMA_MODEL}")
        client = get_client()
        
        logger.debug("Sending chat request to Ollama")
        response = await client.chat(model=OLLAMA_MODEL, messages=[{
            'role': user,
            'content': prompt,
        }])
        
        response_content = response['message']['content']
        logger.debug(f"Received response from Ollama - Length: {len(response_content)} characters")
        
        elapsed_time = time.time() - start_time
        logger.info(f"LLM request completed successfully in {elapsed_time:.2f} seconds - Response length: {len(response_content)} characters")
        
        return response_content
        
    except ConnectionError as e:
        logger.error(f"Connection error to Ollama: {e}")
        raise ConnectionError("Could not connect to Ollama, please ensure Ollama is running.")
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Unexpected error in LLM request after {elapsed_time:.2f} seconds: {e}")
        raise