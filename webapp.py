"""
Simple web interface for the Telegram Forwarder Bot.
This allows the bot to run as a web service on platforms like Render.
"""

import os
import threading
import logging
import traceback
import asyncio
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
bot_thread = None

def start_bot():
    """Start the bot in a separate thread with its own event loop."""
    global bot
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Check for all required environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    source_id = os.getenv("SOURCE_CHANNEL_ID")
    dest_id = os.getenv("DESTINATION_CHANNEL_ID")
    
    # Log detailed environment information
    logger.info(f"Environment check: TOKEN={'YES' if token else 'NO'}, "
                f"SOURCE_ID={'YES' if source_id else 'NO'}, "
                f"DEST_ID={'YES' if dest_id else 'NO'}")
    
    if not token:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
        
    if not source_id:
        logger.error("No source channel ID provided. Set the SOURCE_CHANNEL_ID environment variable.")
        return
        
    if not dest_id:
        logger.error("No destination channel ID provided. Set the DESTINATION_CHANNEL_ID environment variable.")
        return
    
    try:
        # Create and start the forwarder bot
        logger.info("Starting Telegram Forwarder Bot...")
        logger.info(f"Source channel: {source_id}")
        logger.info(f"Destination channel: {dest_id}")
        
        bot = TelegramForwarder(token)
        bot.start()
        logger.info("Bot started successfully!")
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        # Print detailed exception information
        logger.error(traceback.format_exc())

# Routes
@app.route('/')
def home():
    """Home page - shows bot status."""
    global bot
    status = "Running" if bot else "Not running"
    return jsonify({
        "status": status,
        "bot": "Telegram Forwarder Bot",
        "message": "This web interface keeps the bot running. The bot itself operates in the background."
    })

@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({"status": "healthy"})
    
@app.route('/env-check')
def env_check():
    """Check if all required environment variables are set."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    source_id = os.getenv("SOURCE_CHANNEL_ID")
    dest_id = os.getenv("DESTINATION_CHANNEL_ID")
    
    return jsonify({
        "environment_variables": {
            "TELEGRAM_BOT_TOKEN": "Set" if token else "Missing",
            "SOURCE_CHANNEL_ID": "Set" if source_id else "Missing",
            "DESTINATION_CHANNEL_ID": "Set" if dest_id else "Missing"
        },
        "bot_status": "Running" if bot else "Not running",
        "instructions": "Make sure all environment variables are set in your Render dashboard"
    })

# Start the bot when the app is loaded
# For Flask 2.0+, we need to use a different approach since before_first_request is deprecated
bot_thread = None

@app.route('/start', methods=['GET'])
def start_bot_route():
    """Endpoint to start the bot."""
    global bot_thread
    if not bot_thread or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Bot thread started")
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"})

# Initialize the bot at startup
# Starting the bot when the module is imported - works with both gunicorn and Flask
try:
    # Start bot in a separate thread when the app is imported
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Bot thread started at initialization")
except Exception as e:
    logger.error(f"Failed to start bot at initialization: {e}")

# For direct execution during development
if __name__ == '__main__':
    start_bot()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
