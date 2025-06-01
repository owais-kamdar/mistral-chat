# config.py
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Create necessary directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Document processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_CHUNKS = 5

# Caching and retries
MAX_RETRIES = 3
RETRY_DELAY = 1

# LLM settings
LLM_PORT = 8080
LLM_HOST = "localhost"
LLM_URL = f"http://{LLM_HOST}:{LLM_PORT}/completion"
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE = 0.7
LLM_STOP_WORDS = ["</s>", "Human:", "Assistant:"]
