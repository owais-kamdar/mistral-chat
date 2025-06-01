# llm.py (for llamafile)
import requests
import json
from config import LLM_URL, LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_STOP_WORDS

# Run the LLM server on port 8080
# using mistral-7b-instruct-v0.3-q4_0.llamafile
def run_llm(prompt):
    """Send prompt to the running LLM server."""
    try:
        response = requests.post(
            LLM_URL,
            # use the config values
            json={
                "prompt": prompt,
                "n_predict": LLM_MAX_TOKENS,
                "temperature": LLM_TEMPERATURE,
                "stop": LLM_STOP_WORDS
            }
        )
        response.raise_for_status()
        return response.json()["content"].strip()
    except Exception as e:
        return f"Error: Could not connect to LLM server. Make sure it's running on port 8080. Details: {str(e)}"