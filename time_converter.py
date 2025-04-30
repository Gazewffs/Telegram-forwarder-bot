"""
Time converter module for the Telegram forwarder bot.
This module handles time zone conversions between different formats.
"""
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def convert_time(text):
    """
    Convert time formats in the text.
    Currently supports converting from GMT+14:00 to GMT+5:30.
    
    Args:
        text: The text containing time references
        
    Returns:
        Modified text with converted time references
    """
    if not text:
        return text
    
    # Convert standard GMT+14:00 format
    patterns = [
        # Pattern for "16:29:00" or similar formats
        (r'⏰\s*(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*\(GMT\+\d+(?::\d+)?\))?', handle_time_with_clock),
        # Pattern for explicit GMT+14:00 mentions
        (r'GMT\s*\+\s*14(?::00)?', 'GMT+5:30'),
        # Pattern for time with GMT+14:00 format
        (r'(\d{1,2}):(\d{2})(?::(\d{2}))?\s*\(GMT\+14(?::00)?\)', handle_time_with_gmt),
        # General time conversion without specific format mention
        (r'(\d{1,2}):(\d{2})(?::(\d{2}))?', r'\1:\2\3 (GMT+5:30)'),
    ]
    
    result = text
    for pattern, replacement in patterns:
        if callable(replacement):
            # Use a function to handle complex replacements
            result = re.sub(pattern, replacement, result)
        else:
            # Simple string replacement
            result = re.sub(pattern, replacement, result)
    
    return result

def handle_time_with_clock(match):
    """Handle time format with clock emoji."""
    hour = match.group(1)
    minute = match.group(2)
    second = match.group(3) if match.group(3) else "00"
    
    # Format with GMT+5:30
    time_str = f"⏰ {hour}:{minute}"
    if second != "00":
        time_str += f":{second}"
    time_str += " (GMT+5:30)"
    
    return time_str

def handle_time_with_gmt(match):
    """Handle time format that already includes GMT."""
    hour = match.group(1)
    minute = match.group(2)
    second = match.group(3) if match.group(3) else "00"
    
    # Format with GMT+5:30
    time_str = f"{hour}:{minute}"
    if second != "00":
        time_str += f":{second}"
    time_str += " (GMT+5:30)"
    
    return time_str

def adjust_time_zone(hours, minutes, seconds=0, from_gmt=14, to_gmt_hours=5, to_gmt_minutes=30):
    """
    Adjust time from one GMT zone to another.
    Not currently used but added for future enhancements.
    
    Args:
        hours: Hour value (0-23)
        minutes: Minute value (0-59)
        seconds: Second value (0-59)
        from_gmt: Source GMT offset in hours
        to_gmt_hours: Target GMT hour offset
        to_gmt_minutes: Target GMT minute offset
        
    Returns:
        Tuple of (hour, minute, second) in the target time zone
    """
    try:
        # Create a base time
        base_time = datetime(2025, 1, 1, int(hours), int(minutes), int(seconds))
        
        # Adjust for source GMT
        utc_time = base_time - timedelta(hours=from_gmt)
        
        # Adjust for target GMT
        target_time = utc_time + timedelta(hours=to_gmt_hours, minutes=to_gmt_minutes)
        
        return (target_time.hour, target_time.minute, target_time.second)
    except Exception as e:
        logger.error(f"Error adjusting time zone: {e}")
        # Return original time on error
        return (hours, minutes, seconds)