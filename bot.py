import time
import logging
import asyncio
import os
import json
import re
from typing import Dict, Any, Optional, List, Union

from telegram import Bot, Update, Message, Chat
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext,
    ConversationHandler
)
from telegram.error import TelegramError, RetryAfter

import config
from filters import apply_text_filters, create_custom_filter
from image_processor import process_image, should_replace_image, get_replacement_image
from utils import retry_on_error

logger = logging.getLogger(__name__)

class TelegramForwarder:
    """
    Class to handle the forwarding of messages from a source channel to a destination channel
    with customizable modifications.
    """
    
    def __init__(self, token: str):
        """Initialize the TelegramForwarder with the bot token."""
        self.token = token
        self.application = Application.builder().token(token).build()
        self.bot = self.application.bot
        
        # Set up the handlers
        self.setup_handlers()
        
        # Store message history to avoid duplicates
        self.processed_messages = set()
        
        logger.info("Telegram Forwarder initialized")
    
    def setup_handlers(self):
        """Set up the command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        
        # Filter management commands
        self.application.add_handler(CommandHandler("filters", self.cmd_filters))
        self.application.add_handler(CommandHandler("addfilter", self.cmd_add_filter))
        self.application.add_handler(CommandHandler("delfilter", self.cmd_del_filter))
        self.application.add_handler(CommandHandler("testfilter", self.cmd_test_filter))
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
        
        # Message handler for the source channel
        source_channel_id = os.getenv("SOURCE_CHANNEL_ID")
        if source_channel_id:
            source_filter = filters.Chat(chat_id=int(source_channel_id)) & ~filters.COMMAND
            self.application.add_handler(MessageHandler(source_filter, self.handle_channel_message))
        else:
            logger.error("No SOURCE_CHANNEL_ID environment variable set.")
        
        logger.info("Handlers set up")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command."""
        await update.message.reply_text(
            "Hello! I am a channel message forwarder bot. I forward messages from a source "
            "channel to a destination channel with customizable modifications."
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command."""
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Check bot status and configuration\n"
            "/filters - List all active text filters\n"
            "/addfilter - Add a new text filter (usage: /addfilter pattern replacement)\n"
            "/delfilter - Delete a filter by index (usage: /delfilter 1)\n"
            "/testfilter - Test how a message would be filtered (usage: /testfilter your text here)\n\n"
            "The bot forwards messages automatically from the configured source channel to "
            "the destination channel with any defined text and image modifications."
        )
        await update.message.reply_text(help_text)
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /status command."""
        source_channel_name = "Unknown"
        destination_channel_name = "Unknown"
        
        # Try to get channel names
        try:
            source_channel_id = os.getenv("SOURCE_CHANNEL_ID")
            if source_channel_id:
                source_chat = await self.bot.get_chat(int(source_channel_id))
                source_channel_name = source_chat.title or source_chat.username or "Unknown"
            
            destination_channel_id = os.getenv("DESTINATION_CHANNEL_ID")
            if destination_channel_id:
                dest_chat = await self.bot.get_chat(int(destination_channel_id))
                destination_channel_name = dest_chat.title or dest_chat.username or "Unknown"
        except Exception as e:
            logger.warning(f"Failed to get channel names: {e}")
        
        status_text = (
            f"Bot Status: Running\n\n"
            f"Source Channel: {source_channel_name}\n"
            f"Destination Channel: {destination_channel_name}\n\n"
            f"Text Filters: {len(config.TEXT_FILTERS)} active\n"
            f"Image Processing: {'Enabled' if config.IMAGE_PROCESSING['resize']['enabled'] else 'Disabled'}\n\n"
            f"Messages processed: {len(self.processed_messages)}"
        )
        
        await update.message.reply_text(status_text)
    
    @retry_on_error
    async def handle_channel_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle and forward messages from the source channel."""
        message = update.effective_message
        
        # Skip already processed messages
        if message.message_id in self.processed_messages:
            logger.debug(f"Message {message.message_id} already processed, skipping")
            return
        
        # Determine message type
        message_type = "text"
        if message.photo:
            message_type = "photo"
        elif message.video:
            message_type = "video"
        elif message.audio:
            message_type = "audio"
        elif message.document:
            message_type = "document"
        elif message.voice:
            message_type = "voice"
        elif message.sticker:
            message_type = "sticker"
        elif message.poll:
            message_type = "poll"
        elif message.animation:
            message_type = "animation"
            
        logger.info(f"Received message of type {message_type} from source channel")
        
        try:
            # Forward the message with modifications
            await self.forward_message_with_modifications(message)
            
            # Add to processed messages
            self.processed_messages.add(message.message_id)
            
            # Keep the processed messages set from growing too large
            if len(self.processed_messages) > 1000:
                # Remove oldest message IDs (assuming newer IDs are larger)
                self.processed_messages = set(sorted(self.processed_messages)[-1000:])
                
        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            raise  # Let the retry decorator handle retries
    
    async def forward_message_with_modifications(self, message: Message):
        """Forward a message with modifications to the destination channel."""
        destination_channel_id = os.getenv("DESTINATION_CHANNEL_ID")
        if not destination_channel_id:
            logger.error("No DESTINATION_CHANNEL_ID environment variable set.")
            return
            
        destination_id = int(destination_channel_id)
        
        # Handle different message types
        if message.text:
            # Apply text filters
            modified_text = apply_text_filters(message.text, config.TEXT_FILTERS)
            
            # Send the modified text
            await self.bot.send_message(
                chat_id=destination_id,
                text=modified_text,
                disable_web_page_preview=False,
                disable_notification=False
            )
            logger.info("Forwarded text message with modifications")
            
        elif message.photo:
            # Get the largest photo
            photo = message.photo[-1]
            original_caption = message.caption
            
            # Process the caption
            caption = apply_text_filters(original_caption, config.TEXT_FILTERS) if original_caption else None
            
            # Check if we should replace this image
            if config.IMAGE_REPLACEMENT.get("enabled", False) and should_replace_image(original_caption):
                # Get the replacement image
                replacement_photo = get_replacement_image()
                
                # Modify caption if needed
                if config.IMAGE_REPLACEMENT.get("keep_original_caption", True) and caption:
                    additional_text = config.IMAGE_REPLACEMENT.get("additional_caption_text", "")
                    if additional_text:
                        caption = f"{caption}\n\n{additional_text}"
                else:
                    # Use only the additional text if not keeping original caption
                    caption = config.IMAGE_REPLACEMENT.get("additional_caption_text", "")
                
                # Send the replacement photo
                await self.bot.send_photo(
                    chat_id=destination_id,
                    photo=replacement_photo,
                    caption=caption,
                    disable_notification=False
                )
                logger.info("Forwarded photo with replacement image")
            
            # If not replacing or replacement is disabled, use normal processing
            elif config.IMAGE_PROCESSING["resize"]["enabled"]:
                # Download the photo
                photo_file = await self.bot.get_file(photo.file_id)
                
                # Process the image
                processed_photo = await process_image(photo_file, original_caption)
                
                # Send the processed photo
                await self.bot.send_photo(
                    chat_id=destination_id,
                    photo=processed_photo,
                    caption=caption,
                    disable_notification=False
                )
                logger.info("Forwarded photo with image processing")
            else:
                # Forward the original photo without processing
                await self.bot.send_photo(
                    chat_id=destination_id,
                    photo=photo.file_id,
                    caption=caption,
                    disable_notification=False
                )
                logger.info("Forwarded photo without image processing")
                
        elif message.document:
            # Forward document
            caption = apply_text_filters(message.caption, config.TEXT_FILTERS) if message.caption else None
            
            await self.bot.send_document(
                chat_id=destination_id,
                document=message.document.file_id,
                caption=caption,
                disable_notification=False
            )
            logger.info("Forwarded document")
            
        elif message.video:
            # Forward video
            caption = apply_text_filters(message.caption, config.TEXT_FILTERS) if message.caption else None
            
            await self.bot.send_video(
                chat_id=destination_id,
                video=message.video.file_id,
                caption=caption,
                disable_notification=False
            )
            logger.info("Forwarded video")
            
        elif message.audio:
            # Forward audio
            caption = apply_text_filters(message.caption, config.TEXT_FILTERS) if message.caption else None
            
            await self.bot.send_audio(
                chat_id=destination_id,
                audio=message.audio.file_id,
                caption=caption,
                disable_notification=False
            )
            logger.info("Forwarded audio")
            
        elif message.voice:
            # Forward voice
            caption = apply_text_filters(message.caption, config.TEXT_FILTERS) if message.caption else None
            
            await self.bot.send_voice(
                chat_id=destination_id,
                voice=message.voice.file_id,
                caption=caption,
                disable_notification=False
            )
            logger.info("Forwarded voice")
            
        elif message.animation:
            # Forward animation (GIF)
            caption = apply_text_filters(message.caption, config.TEXT_FILTERS) if message.caption else None
            
            await self.bot.send_animation(
                chat_id=destination_id,
                animation=message.animation.file_id,
                caption=caption,
                disable_notification=False
            )
            logger.info("Forwarded animation")
            
        elif message.sticker:
            # Forward sticker
            await self.bot.send_sticker(
                chat_id=destination_id,
                sticker=message.sticker.file_id,
                disable_notification=False
            )
            logger.info("Forwarded sticker")
            
        elif message.poll:
            # Forward poll
            question = apply_text_filters(message.poll.question, config.TEXT_FILTERS)
            options = [apply_text_filters(option.text, config.TEXT_FILTERS) for option in message.poll.options]
            
            await self.bot.send_poll(
                chat_id=destination_id,
                question=question,
                options=options,
                is_anonymous=message.poll.is_anonymous,
                type=message.poll.type,
                allows_multiple_answers=message.poll.allows_multiple_answers,
                disable_notification=False
            )
            logger.info("Forwarded poll")
            
        else:
            # Unknown message type
            logger.warning(f"Unsupported message type encountered")
            
            # Try to forward as is
            modified_text = "Unsupported message type. Original message could not be processed."
            await self.bot.send_message(
                chat_id=destination_id,
                text=modified_text,
                disable_notification=False
            )
            logger.info("Sent fallback message for unsupported message type")
    
    async def cmd_filters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all active text filters."""
        if not config.TEXT_FILTERS:
            await update.message.reply_text("No text filters are currently active.")
            return
            
        reply = "Active text filters:\n\n"
        
        for i, filter_item in enumerate(config.TEXT_FILTERS, 1):
            pattern = filter_item.get("pattern", "")
            replacement = filter_item.get("replacement", "")
            
            # Escape special characters for display
            pattern_display = pattern.replace(r"\n", "↵").replace(r"\t", "→")
            replacement_display = replacement.replace(r"\n", "↵").replace(r"\t", "→")
            
            reply += f"{i}. Pattern: `{pattern_display}`\n   Replace with: `{replacement_display}`\n\n"
            
        await update.message.reply_text(reply, parse_mode="Markdown")
    
    async def cmd_add_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a new text filter."""
        # Check if we have enough arguments
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /addfilter pattern replacement\n\n"
                "Example: `/addfilter hello world` - Replaces 'hello' with 'world'\n"
                "For regex patterns, use Python syntax. Example: `/addfilter \\bhi\\b hey`\n"
                "For newlines in replacement, use \\n. Example: `/addfilter hi hello\\nworld`",
                parse_mode="Markdown"
            )
            return
            
        # Extract pattern and replacement
        pattern = context.args[0]
        replacement = " ".join(context.args[1:])
        
        # Convert escaped characters
        replacement = replacement.replace("\\n", "\n").replace("\\t", "\t")
        
        try:
            # Validate regex pattern by trying to compile it
            re.compile(pattern)
            
            # Create and add the filter
            new_filter = create_custom_filter(pattern, replacement)
            config.TEXT_FILTERS.append(new_filter)
            
            await update.message.reply_text(
                f"Filter added successfully!\n\n"
                f"Pattern: `{pattern}`\n"
                f"Replacement: `{replacement}`",
                parse_mode="Markdown"
            )
            logger.info(f"Added new filter: {pattern} -> {replacement}")
            
        except re.error as e:
            await update.message.reply_text(
                f"Error in regex pattern: {e}\n\n"
                f"Please check your pattern and try again."
            )
    
    async def cmd_del_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete a filter by index."""
        if not context.args:
            await update.message.reply_text(
                "Usage: /delfilter <index>\n\n"
                "Use /filters to see the indices of all active filters."
            )
            return
            
        try:
            # Convert the index from 1-based (user-facing) to 0-based (internal)
            index = int(context.args[0]) - 1
            
            if index < 0 or index >= len(config.TEXT_FILTERS):
                await update.message.reply_text(
                    f"Invalid filter index. Please use a number between 1 and {len(config.TEXT_FILTERS)}."
                )
                return
                
            # Get the filter details for confirmation message
            removed_filter = config.TEXT_FILTERS.pop(index)
            pattern = removed_filter.get("pattern", "")
            replacement = removed_filter.get("replacement", "")
            
            await update.message.reply_text(
                f"Filter removed successfully!\n\n"
                f"Pattern: `{pattern}`\n"
                f"Replacement: `{replacement}`",
                parse_mode="Markdown"
            )
            logger.info(f"Removed filter: {pattern} -> {replacement}")
            
        except ValueError:
            await update.message.reply_text("Please provide a valid number for the filter index.")
    
    async def cmd_test_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test how a message would be filtered."""
        if not context.args:
            await update.message.reply_text(
                "Usage: /testfilter <text>\n\n"
                "Example: `/testfilter Hello world`\n"
                "This will show you how your text would be modified by the active filters.",
                parse_mode="Markdown"
            )
            return
            
        # Get the input text
        input_text = " ".join(context.args)
        
        # Apply the filters
        output_text = apply_text_filters(input_text, config.TEXT_FILTERS)
        
        if input_text == output_text:
            await update.message.reply_text(
                f"Original: `{input_text}`\n\n"
                f"No changes were made - none of your filters matched this text.",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"Original: `{input_text}`\n\n"
                f"Filtered: `{output_text}`",
                parse_mode="Markdown"
            )

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the dispatcher."""
        try:
            if update and isinstance(update, Update) and update.effective_message:
                # Extract error information
                error = context.error
                
                if isinstance(error, RetryAfter):
                    logger.warning(f"Rate limited. Retrying in {error.retry_after} seconds")
                    await asyncio.sleep(error.retry_after)
                    # The retry decorator will handle retrying
                else:
                    logger.error(f"Error processing update {update}: {error}")
            else:
                logger.error(f"Update {update} caused error: {context.error}")
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    def start(self):
        """Start the bot."""
        logger.info("Starting the bot...")
        
        # Run the bot until the user presses Ctrl-C
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
