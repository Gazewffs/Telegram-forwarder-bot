#!/usr/bin/env python3
"""
Standalone Telegram Forwarder Bot for VPS/Termux deployment.
This version runs without the web interface for simpler deployment.
"""

import logging
import os
from bot import TelegramForwarder

# Configure logging with timestamp
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """Main function to start the Telegram forwarder bot."""
    # Get the bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("No token provided! Set the TELEGRAM_BOT_TOKEN environment variable.")
        logger.error("Example: export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return

    # Check for source and destination channels
    source_id = os.getenv("SOURCE_CHANNEL_ID")
    dest_id = os.getenv("DESTINATION_CHANNEL_ID")
    
    if not source_id or not dest_id:
        logger.error("Channel IDs not set! Please set SOURCE_CHANNEL_ID and DESTINATION_CHANNEL_ID.")
        logger.error("Example: export SOURCE_CHANNEL_ID='-1001234567890'")
        logger.error("Example: export DESTINATION_CHANNEL_ID='-1009876543210'")
        return
    
    try:
        # Create and start the forwarder bot
        logger.info(f"Starting Telegram Forwarder Bot...")
        logger.info(f"Source channel: {source_id}")
        logger.info(f"Destination channel: {dest_id}")
        
        forwarder = TelegramForwarder(token)
        forwarder.start()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()