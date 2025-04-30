import logging
import os
import threading
from bot import TelegramForwarder
from webapp import app

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def run_bot():
    """Function to run the telegram bot in a separate thread."""
    # Get the bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    try:
        # Create and start the forwarder bot
        forwarder = TelegramForwarder(token)
        forwarder.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

def main():
    """Main function to start the bot and web interface."""
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # For Gunicorn/Workflow usage, we export the app variable
    return app

# For direct python execution
if __name__ == '__main__':
    # When running as a script, just run the bot
    run_bot()
