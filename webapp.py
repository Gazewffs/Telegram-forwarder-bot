"""
Simple web interface for the Telegram Forwarder Bot.
This allows the bot to run as a web service on platforms like Render.
"""

import os
import threading
import logging
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
    """Start the bot in a separate thread."""
    global bot
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    try:
        # Create and start the forwarder bot
        logger.info("Starting Telegram Forwarder Bot...")
        bot = TelegramForwarder(token)
        bot.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

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