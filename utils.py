# utils.py
import time
from config import MAX_RETRIES, RETRY_DELAY

def retry(func):
    """Retry decorator with exponential backoff."""
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(RETRY_DELAY * (2 ** attempt))
    return wrapper
