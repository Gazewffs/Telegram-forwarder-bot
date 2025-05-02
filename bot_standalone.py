"""
Standalone app for running the Telegram Forwarder Bot on Render.
This version runs the bot directly rather than in a separate thread.
"""

import os
import logging
import asyncio
import threading
from flask import Flask, jsonify
from bot import TelegramForwarder

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Bot instance
bot = None
bot_running = False

def async_bot_start():
    """Run the bot in an event loop."""
    global bot, bot_running
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Get environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    source_id = os.getenv("SOURCE_CHANNEL_ID")
    dest_id = os.getenv("DESTINATION_CHANNEL_ID")
    
    # Detailed logging
    logger.info(f"Starting bot with TOKEN={'Present' if token else 'Missing'}")
    logger.info(f"Source channel ID: {source_id}")
    logger.info(f"Destination channel ID: {dest_id}")
    
    try:
        # Create the bot
        bot = TelegramForwarder(token)
        # Start the bot
        logger.info("Starting bot...")
        bot.start()
        bot_running = True
        logger.info("Bot started successfully!")
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        bot_running = False

# Start bot in a thread
def start_bot_thread():
    thread = threading.Thread(target=async_bot_start)
    thread.daemon = True
    thread.start()
    return thread

# Start the bot when app is imported
bot_thread = start_bot_thread()

# Routes
@app.route('/')
def home():
    """Home page."""
    return jsonify({
        "status": "Bot is running" if bot_running else "Bot failed to start",
        "message": "Check /env-check for more details"
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

@app.route('/env-check')
def env_check():
    """Check environment variables."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    source_id = os.getenv("SOURCE_CHANNEL_ID", "")
    dest_id = os.getenv("DESTINATION_CHANNEL_ID", "")
    
    # Check if any variables are empty or have improper format
    token_status = "Set" if token else "Missing"
    
    source_id_status = "Set"
    if not source_id:
        source_id_status = "Missing"
    elif not (source_id.startswith("-100") and source_id[4:].isdigit()):
        source_id_status = "Incorrect format (should start with -100 for channels)"
    
    dest_id_status = "Set"
    if not dest_id:
        dest_id_status = "Missing"
    elif not (dest_id.startswith("-100") and dest_id[4:].isdigit()):
        dest_id_status = "Incorrect format (should start with -100 for channels)"
    
    return jsonify({
        "environment_variables": {
            "TELEGRAM_BOT_TOKEN": token_status,
            "SOURCE_CHANNEL_ID": source_id_status,
            "DESTINATION_CHANNEL_ID": dest_id_status
        },
        "bot_status": "Running" if bot_running else "Not running",
        "instructions": "Make sure all channel IDs begin with -100 for Telegram supergroups and channels"
    })

@app.route('/restart')
def restart_bot():
    """Restart the bot."""
    global bot_thread, bot_running, bot
    
    # Stop the old thread if it exists
    bot_running = False
    
    # Start a new thread
    bot_thread = start_bot_thread()
    
    return jsonify({
        "status": "Bot restart initiated",
        "message": "Check the logs for details"
    })

# For direct execution
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
