# config.py
"""
Configuration settings for the Telegram Forwarder Bot.
This file contains configurations for text filters, image processing, and other settings.
"""

# Text filters configuration
# Each filter consists of a pattern (regular expression) and replacement
TEXT_FILTERS = [
    {"pattern": r"#(\w+)", "replacement": r"#\1 #forwarded"},  # Add #forwarded to hashtags
    {"pattern": r"(?i)\b(bad|offensive)\b", "replacement": "****"},  # Censor offensive words
    {"pattern": r"@channel", "replacement": ""},  # Remove channel mentions
    # Replace registration text with money management message
    {"pattern": r"➪ REGISTER HERE \| إنــضــم إلـى فــريقـي\n➪ Code: \( 9oNvFZEQya \) 50% Deposit bounus", 
     "replacement": r"➪ Use MTG 1 Step If Loss .\n➪ Always Use Proper Money Management To Avoid losses*"},
    # Simplified version in case the exact format varies
    {"pattern": r".*REGISTER HERE.*\n.*Code: \(.*\).*Deposit.*", 
     "replacement": r"➪ Use MTG 1 Step If Loss .\n➪ Always Use Proper Money Management To Avoid losses*"}
    # Time conversion is now handled directly in filters.py
]

# Image processing configuration
IMAGE_PROCESSING = {
    "resize": {
        "enabled": True,
        "max_width": 1200,
        "max_height": 1200,
        "keep_aspect_ratio": True
    },
    "enhancements": {
        "enabled": True,
        "brightness": 1.1,  # Slight brightness increase (1.0 is normal)
        "contrast": 1.05,   # Slight contrast increase
        "sharpness": 1.2    # Moderate sharpness increase
    },
    "watermark": {
        "enabled": True,
        "text": "Forwarded",
        "position": "bottom-right",  # Options: top-left, top-right, bottom-left, bottom-right, center
        "font_size": 30,
        "font_color": (255, 255, 255, 128)  # RGBA
    }
}

# Image replacement configuration
IMAGE_REPLACEMENT = {
    "enabled": True,
    "replace_all_images": False,       # Setting to False - only replace images with captions
    "replace_only_with_caption": True, # New setting - only replace images that have captions
    "replacement_path": "assets/replacement_image.jpg",  # Path to the replacement image
    # List of patterns to match in image captions or surrounding text to identify images to replace
    "patterns_to_match": [
        r"(?i)QTX",
        r"(?i)Tarek",
        r"EURUSD",
        r"@Gazew_07-1M",
        r"https://bit.ly/TarekQTXTeam"
    ],
    # Whether to keep the original caption when replacing an image
    "keep_original_caption": True,
    # Additional caption text to append to original caption when replacing an image
    "additional_caption_text": ""
}

# Bot behavior settings
BOT_SETTINGS = {
    "allowed_message_types": ["text", "photo", "video", "document", "audio", "poll", "sticker"],
    "max_retry_attempts": 3,
    "retry_delay_seconds": 5,
}