import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar, cast
import time

T = TypeVar('T')
logger = logging.getLogger(__name__)

def retry_on_error(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to retry functions on specific errors with exponential backoff.
    
    Args:
        func: The async function to decorate
        
    Returns:
        Decorated function with retry logic
    """
    from config import BOT_SETTINGS
    
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        max_attempts = BOT_SETTINGS.get("max_retry_attempts", 3)
        base_delay = BOT_SETTINGS.get("retry_delay_seconds", 5)
        
        for attempt in range(1, max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Log the error
                logger.error(f"Error in {func.__name__}: {e}")
                
                # If this was the last attempt, re-raise the exception
                if attempt == max_attempts:
                    logger.error(f"Max retry attempts ({max_attempts}) reached for {func.__name__}")
                    raise
                
                # Calculate delay with exponential backoff
                delay = base_delay * (2 ** (attempt - 1))
                logger.info(f"Retrying {func.__name__} in {delay} seconds (attempt {attempt}/{max_attempts})")
                await asyncio.sleep(delay)
        
        # This should never be reached due to the re-raise above
        return cast(T, None)
    
    return wrapper

def format_time_delta(seconds: int) -> str:
    """
    Format seconds into a human-readable time string.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string (e.g., "2h 30m 15s")
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def safely_get_chat_info(chat_obj: Any) -> str:
    """
    Safely extract chat information without raising exceptions.
    
    Args:
        chat_obj: Telegram Chat object
        
    Returns:
        String with chat information
    """
    if not chat_obj:
        return "Unknown"
    
    try:
        if hasattr(chat_obj, "title") and chat_obj.title:
            return f"{chat_obj.title} (ID: {chat_obj.id})"
        elif hasattr(chat_obj, "username") and chat_obj.username:
            return f"@{chat_obj.username} (ID: {chat_obj.id})"
        elif hasattr(chat_obj, "first_name"):
            name = chat_obj.first_name
            if hasattr(chat_obj, "last_name") and chat_obj.last_name:
                name += f" {chat_obj.last_name}"
            return f"{name} (ID: {chat_obj.id})"
        else:
            return f"Chat (ID: {chat_obj.id})"
    except Exception as e:
        logger.error(f"Error extracting chat info: {e}")
        return "Unknown chat"