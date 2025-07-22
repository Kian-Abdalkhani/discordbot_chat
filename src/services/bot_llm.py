from httpx import HTTPError, HTTPStatusError
from ollama import Client
from ollama import ChatResponse
import os
import asyncio

#enter the model from ollama that you would like to use and connect to Ollama:
OLLAMA_MODEL: str="boug_bot:HC"

# Only create the client when needed, not at import time
def get_client():
    return Client(host=os.getenv("OLLAMA_API_URL"))

async def bot_response(user: str = "user", prompt: str = "") -> str:
    # ... validation code ...
    
    def _sync_llm_call():
        client = get_client()
        response = client.chat(model=OLLAMA_MODEL, messages=[{
            'role': user,
            'content': prompt,
        }])
        return response['message']['content']
    
    try:
        # Run the blocking operation in a thread pool
        return await asyncio.to_thread(_sync_llm_call)
    except ConnectionError:
        raise ConnectionError("Could not connect to Ollama, please ensure Ollama is running.")