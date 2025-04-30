import re
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def convert_time_format(text: str) -> str:
    """
    Convert time formats from GMT+14:00 to GMT+5:30.
    
    This handles specific patterns found in the messages, including:
    - Clock emoji with time
    - Time followed by GMT+14:00
    - Other time formats
    
    Args:
        text: The text containing time references
        
    Returns:
        Text with converted time references
    """
    if not text:
        return text
    
    # Pattern 1: Match "🕒 16:29:00" or similar formats with clock emoji
    text = re.sub(
        r'(🕒|⏰|⌚️)\s*(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*\(GMT\+\d+(?::\d+)?\))?',
        lambda m: format_clock_emoji_time(m.group(1), m.group(2), m.group(3), m.group(4)),
        text
    )
    
    # Pattern 2: Handle time specifically mentioned with GMT+14:00 format
    text = re.sub(
        r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*(?:\(GMT\+14(?::00)?\))',
        lambda m: format_time_with_new_gmt(m.group(1), m.group(2), m.group(3)),
        text
    )
    
    # Pattern 3: Make sure all GMT formats are consistent
    text = re.sub(r'GMT\s*\+\s*\d+(?::\d+)?', 'GMT+14:00', text)
    
    # Pattern 4: Handle typical forex signal format with EURUSD and other pairs
    eurusd_pattern = re.search(r'((?:EUR|USD|GBP|JPY|AUD|NZD|CAD|CHF){2})(?:\s*\n\s*)?(🕒|⏰|⌚️)?(?:\s*\n\s*)?(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*\(GMT\+\d+(?::\d+)?\))?(?:\s*\n\s*)?(?:M1|M5|M15|M30|H1|H4|D1)?', text)
    
    if eurusd_pattern:
        pair = eurusd_pattern.group(1)
        time_hour = eurusd_pattern.group(3)
        time_min = eurusd_pattern.group(4)
        time_frame = "M1"  # Default timeframe
        
        # Look for timeframe in the text
        timeframe_match = re.search(r'(M1|M5|M15|M30|H1|H4|D1)', text)
        if timeframe_match:
            time_frame = timeframe_match.group(1)
            
        # Create the formatted signal message
        formatted_signal = f"{pair}\n🕒 {time_hour}:{time_min} (GMT+14:00)\n{time_frame}"
        
        # Replace the entire signal pattern
        text = re.sub(
            r'(?:EUR|USD|GBP|JPY|AUD|NZD|CAD|CHF){2}.*?(?:M1|M5|M15|M30|H1|H4|D1)',
            formatted_signal,
            text,
            flags=re.DOTALL
        )
    
    return text

def format_clock_emoji_time(emoji: str, hour: str, minute: str, second: str | None = None) -> str:
    """Format time with clock emoji and GMT+14:00."""
    time_str = f"{emoji} {hour}:{minute}"
    if second:
        time_str += f":{second}"
    time_str += " (GMT+14:00)"
    return time_str

def format_time_with_new_gmt(hour: str, minute: str, second: str | None = None) -> str:
    """Format time with GMT+14:00."""
    time_str = f"{hour}:{minute}"
    if second:
        time_str += f":{second}"
    time_str += " (GMT+14:00)"
    return time_str

def apply_text_filters(text: str, filters: List[Dict[str, str]]) -> str:
    """
    Apply text filters to modify the text content.
    
    Args:
        text: The original text message
        filters: List of filter dictionaries with 'pattern' and 'replacement' keys
        
    Returns:
        Modified text after applying all filters
    """
    if not text:
        return text
    
    # First convert time formats
    modified_text = convert_time_format(text)
    
    # Then apply other filters
    for filter_item in filters:
        pattern = filter_item.get("pattern")
        replacement = filter_item.get("replacement")
        
        if not pattern or replacement is None:
            continue
        
        try:
            modified_text = re.sub(pattern, replacement, modified_text)
        except Exception as e:
            # Log the error but continue processing other filters
            logger.error(f"Error applying filter {pattern}: {e}")
    
    return modified_text

def create_custom_filter(pattern: str, replacement: str) -> Dict[str, str]:
    """
    Create a custom text filter.
    
    Args:
        pattern: Regular expression pattern to match
        replacement: Replacement string or pattern
        
    Returns:
        A filter dictionary for use with apply_text_filters
    """
    return {
        "pattern": pattern,
        "replacement": replacement
    }