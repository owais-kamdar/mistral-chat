# logger.py
from loguru import logger
from config import LOG_FILE

# Remove default handler (which outputs to stderr)
logger.remove()

# Only log to file
logger.add(LOG_FILE, format="{time} | {level} | {message}")
